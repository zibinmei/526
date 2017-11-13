#include <stdio.h>

void arrstrcpy(char *s, char *t){
	int i =0;
	while (t[i]!='\0'){
		s[i]=t[i];
		i=i+1;
		}
	if (t[i]=='\0'){
		s[i]='\0';
	}
}
	
	
	






int main(){

	char original[]="get packed";
	char copy[]="hello world";
	
	arrstrcpy(copy, original);
	printf("%s \n", copy);
	return 0;
}
