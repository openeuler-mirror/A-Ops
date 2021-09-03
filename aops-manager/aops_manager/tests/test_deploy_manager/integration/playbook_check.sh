#/bin/bash

CheckPlaybook() {

  playbook_file=$1
  echo -e "\n===================Check $playbook_file ==========================="
  ansible-lint --force-color --offline -p $playbook_file
}

CheckAllPlaybooks() {
  playbook_path=$1
  if [ ! -d $playbook_path ]; then
    echo "[ERROR] The playbook_path $playbook_path not existed."
    exit 1
  fi

  filelist=$(find $playbook_path -name *.yml)
  for file in $filelist; do
    if test -f $file; then
      CheckPlaybook $file
    else
      echo "[ERROR] $file is not a yaml file"
    fi
  done

}

PLAYBOOK_PATH="../../../../aops_manager/deploy_manager/ansible_handler/playbooks"

CheckAllPlaybooks $PLAYBOOK_PATH
