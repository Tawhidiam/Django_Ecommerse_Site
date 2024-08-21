 echo "BUILD START"
 python3.11 -m pip install -r list.txt
 python3.11 manage.py collectstatic --noinput --clear
 echo "BUILD END"