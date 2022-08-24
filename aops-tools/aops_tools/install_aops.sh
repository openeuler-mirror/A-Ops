#!/bin/bash
CURRENT_PATH=$(dirname $0)
INVENTORY_PATH=$(realpath ${CURRENT_PATH}/ansible_handler/inventory)
INVENTORY_OUT_PUT=$(realpath ${CURRENT_PATH}/output)
ANSIBLE_CONFIG_FILE=/etc/ansible/ansible.cfg

install_dependency_pkg(){
    echo "[Info]Start install dependency packages."

    # Install ansible
    pkg_list=("ansible" "python3-pandas" "python3-xlrd")
    for i in ${pkg_list[*]}; do
        yum install $i -y
        if [ $? -ne 0 ]; then
          echo "[Error]Install $i failed!"
          return 1
        fi
    done

    # Modify ansible config

    if [ ! -f "$ANSIBLE_CONFIG_FILE" ]; then
       echo "[Warning]$ansible_config_file not exist."
       return 1
    fi
    sed -i 's/#host_key_checking = False/host_key_checking = False/g' $ANSIBLE_CONFIG_FILE

}


build_inventory() {
    echo "[Info]Start build inventory"
    mkdir -p $INVENTORY_PATH/
    python3 build_inventory.py

    # shellcheck disable=SC2115
    rm -rf $INVENTORY_PATH/*
    rm -rf $INVENTORY_OUT_PUT

    python3 build_inventory.py
    if [ $? -ne 0 ] || [ ! -d $INVENTORY_OUT_PUT ]; then
       echo "[Error]$INVENTORY_OUT_PUT not exist. Build inventory failed!"
       return 1
    fi
    cp $INVENTORY_OUT_PUT/* $INVENTORY_PATH/
    rm -rf $INVENTORY_OUT_PUT

}

deploy_by_ansible() {
  echo "[Info]Start deploy pkg by ansible."
  pkg_list=("aops_agent")
  for i in ${pkg_list[*]}; do
      ansible-playbook -i ansible_handler/inventory/$i ansible_handler/playbooks/$i.yml
      if [ $? -ne 0 ]; then
        echo "[Error]Ansible execute $i failed!"
        return 1
      fi
  done
}


main(){
    install_dependency_pkg
    if [ $? -ne 0 ]; then
      echo "[Error]Install dependency package failed!"
      exit 1
    else
      echo "[Info]Build dependency package succeed!"
    fi

    build_inventory
    if [ $? -ne 0 ]; then
      echo "[Error]Build inventory failed!"
      exit 1
    else
      echo "[Info]Build inventory succeed!"
    fi

    deploy_by_ansible
    ret=$? 
    rm -rf $INVENTORY_PATH/*
    if [ $ret -ne 0 ]; then
      echo "[Error]Deploy package by ansible failed!"
      exit 1
    else
      echo "[Info]Deploy package by ansible succeed!"
    fi
}

main
