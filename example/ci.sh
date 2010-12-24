cd $WORKSPACE
virtualenv ve
. ve/bin/activate
python setup.py develop
pip install -r requirements.txt
pip install -e git://github.com/kmmbvnr/django-hudson.git#egg=django-hudson
cd example
python manage.py hudson --settings=test_settings
