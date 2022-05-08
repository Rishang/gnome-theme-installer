.ONESHELL: # Applies to every targets in the file! https://www.gnu.org/software/make/manual/html_node/One-Shell.html

URL="https://www.gnome-look.org/s/Gnome/p/1253385/"
# URL=https://www.gnome-look.org/p/1403328

export TEST_THEME_INSTALLER=true

run:
	python3 cli.py get ${URL}

ls:
	python3 cli.py ls -t

rm:
	python3 cli.py rm -t

update:
	python3 cli.py update -t

sudo_run:
	sudo python3 cli.py get ${URL}
