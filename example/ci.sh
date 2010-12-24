cd $WORKSPACE
virtualenv ve
. ve/bin/activate
python setup.py develop
pip install -r requirements.txt
pip install django_hudson
cp -r example/settings.py example/test_settings.py
echo 'INSTALLED_APPS += ("django_hudson", )' >> example/test_settings.py
cd example
python manage.py hudson --settings=test_settings
