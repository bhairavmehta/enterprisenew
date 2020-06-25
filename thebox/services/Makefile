
all: package

ifeq ($(OS),Windows_NT)
package: package_win
else
package: package_linux
endif

package_win:
	.\build_dist.cmd

package_linux:
	bash ./build_dist.sh



