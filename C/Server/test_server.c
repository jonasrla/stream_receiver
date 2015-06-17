#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
// #include "opencv2/highgui/highgui.hpp"
#include "server.h"
// using namespace cv;


int main(int argc, char *argv[]) {
    int socket, *sockfd, n, *size;
    size = (int*) malloc(sizeof(int));
    sockfd = (int*) malloc(sizeof(int));
    // cvNamedWindow( "result", 1 );
    if (argc < 2) {
        fprintf(stderr,"ERROR, no port provided\n");
        exit(1);
    }
    socket = create_server(atoi(argv[1]), sockfd);
    request_frame(socket);
    get_frame(socket, size);
    printf("%d\n", *size);
    close(socket);
    close(*sockfd);
    free(sockfd);
    return 0; 
}