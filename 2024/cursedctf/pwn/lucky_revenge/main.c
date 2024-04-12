#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

int main(){
	unsigned int i = 0;
	int number = 0x404000;
	while (i < UINT_MAX){
		srand (i);
		int j = -1;
		int x;
		while (++j < 255){
			x = rand();
			if ( x > 0x404000 && x < (0x404028 + 8)){
				printf("seed %d iteration %d %p\n", i, j, (void *)x);
				if (x % 8 == 0)
					puts("\t\tSo fucking valid");
			}
			j++;
		}
		i++;
	}
	puts("fucking hell");
}
