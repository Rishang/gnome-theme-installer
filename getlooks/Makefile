.ONESHELL: # Applies to every targets in the file! https://www.gnu.org/software/make/manual/html_node/One-Shell.html

URL="https://www.gnome-look.org/s/Gnome/p/1253385/"
# URL=https://www.gnome-look.org/p/1403328

export TEST_THEME_INSTALLER=debug

run:
	uv run gnomelooks get ${URL}

ls:
	uv run gnomelooks ls -t

rm:
	uv run gnomelooks rm -t

update:
	uv run gnomelooks update -t

sudo_run:
	sudo uv run gnomelooks get ${URL}
