#!/usr/bin/env bash
# Zune on-demand AOSP build host on AWS (cost-controlled). Region ap-south-1.
#
#   aws-build-session.sh init           create SSH key + security group (free)
#   aws-build-session.sh init-volume    create the persistent source volume (~USD 14/month, billed while it exists)
#   aws-build-session.sh up [--dry-run] launch the instance, attach the source volume
#   aws-build-session.sh ssh [cmd...]   connect
#   aws-build-session.sh status         instance, volumes, running cost
#   aws-build-session.sh down           terminate the instance (source volume is kept)
#
# Cost controls: instance-initiated shutdown = terminate (root + scratch disks vanish with it);
# hard maximum runtime (MAX_HOURS, default 4); idle watchdog stops it after 15 idle minutes.
# Source tree lives on the persistent volume mounted at /aosp; out/ is a symlink to the throwaway scratch disk (do NOT set OUT_DIR, siso breaks).
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"; export AWS_DEFAULT_REGION="$REGION"
TYPE="${TYPE:-m6a.8xlarge}"          # 32 vCPU / 128 GB; use m8i.8xlarge only for a Cuttlefish/KVM trial
AZ="${AZ:-ap-south-1a}"
SRC_GB="${SRC_GB:-200}"; SCRATCH_GB="${SCRATCH_GB:-300}"; MAX_HOURS="${MAX_HOURS:-4}"
KEY="zune-build"; SG="zune-build-ssh"; PEM="$HOME/.ssh/zune-build.pem"
TAG="zune-build"
AMI_PARAM="/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"

q(){ aws "$@" --output text; }
src_vol(){ q ec2 describe-volumes --filters Name=tag:Name,Values=zune-aosp-src --query 'Volumes[0].VolumeId' | grep -v '^None$' || true; }
instance(){ q ec2 describe-instances --filters Name=tag:Project,Values=$TAG Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].InstanceId'; }
my_ip(){ curl -sSf https://checkip.amazonaws.com | tr -d '\n'; }

cmd_init() {
  if ! aws ec2 describe-key-pairs --key-names "$KEY" >/dev/null 2>&1; then
    umask 077; mkdir -p "$HOME/.ssh"
    aws ec2 create-key-pair --key-name "$KEY" --query KeyMaterial --output text > "$PEM"; chmod 600 "$PEM"
    echo "created key pair $KEY -> $PEM (private key stays on this machine; never commit it)"
  fi
  vpc=$(q ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId')
  if ! aws ec2 describe-security-groups --filters Name=group-name,Values=$SG >/dev/null 2>&1 \
     || [ "$(q ec2 describe-security-groups --filters Name=group-name,Values=$SG --query 'length(SecurityGroups)')" = 0 ]; then
    aws ec2 create-security-group --group-name "$SG" --description "Zune build host SSH from operator IP" --vpc-id "$vpc" >/dev/null
    echo "created security group $SG"
  fi
  echo "init done (no billable resources created)"
}

sg_id(){ q ec2 describe-security-groups --filters Name=group-name,Values=$SG --query 'SecurityGroups[0].GroupId'; }

cmd_init_volume() {
  [ -n "$(src_vol)" ] && { echo "source volume exists: $(src_vol)"; return; }
  v=$(q ec2 create-volume --availability-zone "$AZ" --size "$SRC_GB" --volume-type gp3 \
      --tag-specifications "ResourceType=volume,Tags=[{Key=Name,Value=zune-aosp-src},{Key=Project,Value=$TAG}]" --query VolumeId)
  echo "created $v ($SRC_GB GB gp3 in $AZ), billed ~USD $(python3 -c "print(round($SRC_GB*0.0912,2))")/month until deleted"
}

userdata() {
cat <<EOF
#!/bin/bash
set -x
exec > /var/log/zune-userdata.log 2>&1
SRC_VOL_ID="$1"; MAX_MIN=$((MAX_HOURS*60))
# hard maximum runtime: terminate (shutdown behaviour = terminate) after MAX_HOURS no matter what
shutdown -h +\$MAX_MIN "zune-build max runtime reached" &
# idle watchdog: no ssh users, no build/sync processes, 3 consecutive idle checks (5 min apart)
cat >/usr/local/bin/zune-idle.sh <<'W'
#!/bin/bash
f=/run/zune-idle-count
if [ -n "\$(who)" ] || pgrep -f '/usr/local/bin/repo|git-remote|git fetch|git clone' >/dev/null || pgrep -x 'ninja|soong_ui|soong_build|launch_cvd|cvd_internal_start|rsync|tmux|screen|ccache|clang|rustc|javac|apt-get' >/dev/null; then echo 0 >\$f; exit 0; fi
n=\$(( \$(cat \$f 2>/dev/null || echo 0) + 1 )); echo \$n >\$f
[ \$n -ge 3 ] && shutdown -h now "zune-build idle"
W
chmod +x /usr/local/bin/zune-idle.sh
echo '*/5 * * * * root /usr/local/bin/zune-idle.sh' >/etc/cron.d/zune-idle
# packages (spec 01 section 4.1 baseline)
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git-core gnupg flex bison build-essential zip curl zlib1g-dev libc6-dev-i386 x11proto-core-dev \
  libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip fontconfig python3 rsync libncurses-dev bc ccache tmux
curl -sSf https://storage.googleapis.com/git-repo-downloads/repo -o /usr/local/bin/repo && chmod +x /usr/local/bin/repo
# disks: source volume by volume id; scratch = remaining unmounted nvme disk
id=\$(echo "\$SRC_VOL_ID" | tr -d '-')
for i in \$(seq 1 120); do [ -e /dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_\$id ] && break; sleep 5; done
SRC=\$(readlink -f /dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_\$id)
blkid "\$SRC" >/dev/null 2>&1 || mkfs.ext4 -q -L zune-src "\$SRC"
mkdir -p /aosp /mnt/out; mount "\$SRC" /aosp
SCR=\$(lsblk -dnpo NAME,TYPE,MOUNTPOINT | awk '\$2=="disk" && \$3==""{print \$1}' | grep -vx "\$SRC" | while read d; do lsblk -no MOUNTPOINT "\$d" | grep -q . || echo "\$d"; done | head -1)
[ -n "\$SCR" ] && { mkfs.ext4 -q "\$SCR"; mount "\$SCR" /mnt/out; }
chown -R ubuntu:ubuntu /aosp /mnt/out
# Ubuntu 24.04 blocks unprivileged user namespaces; the AOSP nsjail sandbox needs them (build failed at 84% without this)
sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
# siso fails with an absolute OUT_DIR outside the tree: keep OUT_DIR unset and symlink /aosp/out to the scratch disk
ln -sfn /mnt/out /aosp/out; chown -h ubuntu:ubuntu /aosp/out; mkdir -p /mnt/out/ccache; chown ubuntu:ubuntu /mnt/out/ccache
echo 'export PATH=/usr/local/bin:\$PATH USE_CCACHE=1 CCACHE_EXEC=/usr/bin/ccache CCACHE_DIR=/mnt/out/ccache' >/etc/profile.d/zune-build.sh
touch /run/zune-ready
EOF
}

cmd_up() {
  dry=""; [ "${1:-}" = "--dry-run" ] && dry="--dry-run"
  [ -n "$(instance)" ] && { echo "already running: $(instance)"; return 1; }
  vol=$(src_vol); [ -n "$vol" ] || { echo "no source volume: run init-volume first"; return 1; }
  sg=$(sg_id); ip=$(my_ip)
  aws ec2 authorize-security-group-ingress --group-id "$sg" --protocol tcp --port 22 --cidr "$ip/32" >/dev/null 2>&1 || true
  ami=$(q ssm get-parameter --name "$AMI_PARAM" --query Parameter.Value)
  ud=$(mktemp); userdata "$vol" >"$ud"
  set +e
  out=$(aws ec2 run-instances $dry --image-id "$ami" --instance-type "$TYPE" --key-name "$KEY" --security-group-ids "$sg" \
    --placement "AvailabilityZone=$AZ" --instance-initiated-shutdown-behavior terminate \
    --metadata-options HttpTokens=required --user-data "file://$ud" \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=40,VolumeType=gp3,DeleteOnTermination=true}" \
                            "DeviceName=/dev/sdf,Ebs={VolumeSize=$SCRATCH_GB,VolumeType=gp3,DeleteOnTermination=true}" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=zune-build},{Key=Project,Value=$TAG}]" \
                         "ResourceType=volume,Tags=[{Key=Project,Value=$TAG}]" \
    --query 'Instances[0].InstanceId' --output text 2>&1); rc=$?
  set -e; rm -f "$ud"
  if [ -n "$dry" ]; then echo "$out" | tail -2; return 0; fi
  [ $rc -eq 0 ] || { echo "$out"; return $rc; }
  echo "launched $out; waiting for running state..."
  aws ec2 wait instance-running --instance-ids "$out"
  aws ec2 attach-volume --volume-id "$vol" --instance-id "$out" --device /dev/sdg >/dev/null
  echo "attached $vol. Max runtime ${MAX_HOURS}h, idle shutdown 15 min. Wait ~3 min, then: $0 ssh"
}

cmd_ssh() {
  i=$(instance); [ -n "$i" ] || { echo "no instance"; return 1; }
  host=$(q ec2 describe-instances --instance-ids "$i" --query 'Reservations[0].Instances[0].PublicIpAddress')
  exec ssh -i "$PEM" -o StrictHostKeyChecking=accept-new "ubuntu@$host" "$@"
}

cmd_status() {
  i=$(instance)
  if [ -z "$i" ]; then echo "no build instance (compute cost: 0)"; else
    q ec2 describe-instances --instance-ids "$i" --query 'Reservations[0].Instances[0].[InstanceId,InstanceType,State.Name,LaunchTime,PublicIpAddress]'
    echo "WARNING: instance is billing; run '$0 down' when finished"; fi
  v=$(src_vol); [ -n "$v" ] && q ec2 describe-volumes --volume-ids "$v" --query 'Volumes[0].[VolumeId,Size,State]' || echo "no source volume"
}

cmd_down() {
  i=$(instance); [ -z "$i" ] && { echo "nothing to terminate"; return; }
  aws ec2 terminate-instances --instance-ids "$i" >/dev/null && aws ec2 wait instance-terminated --instance-ids "$i"
  echo "terminated $i; scratch and root disks deleted; source volume kept"
}

c="${1:-}"; shift || true
case "$c" in
  init) cmd_init;; init-volume) cmd_init_volume;; up) cmd_up "$@";; ssh) cmd_ssh "$@";; status) cmd_status;; down) cmd_down;;
  *) sed -n '2,12p' "$0"; exit 1;;
esac
