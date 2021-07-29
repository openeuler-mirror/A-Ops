advisor_path=$(cd $(dirname ${BASH_SOURCE}); pwd)
python_paths=$(echo ${PYTHONPATH} | sed 's/:/ /g')
existed=0
for path in $python_paths
do
	if [ $advisor_path = $path ]; then
		existed=1
	fi
done

if [ $existed -eq 0 ]; then
	export PYTHONPATH=${PYTHONPATH}:${advisor_path}
fi
echo "PYTHONPATH=${PYTHONPATH}"