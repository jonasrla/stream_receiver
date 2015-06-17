#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include "opencv2/highgui/highgui.hpp"

using namespace std;
using namespace cv;

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

int create_server(int portno, int *sockfd){
    int newsockfd;
    socklen_t clilen;
    struct sockaddr_in serv_addr, cli_addr;

    *sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");

    // bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(portno);

    if (bind(*sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) 
        error("ERROR on binding");

    listen(*sockfd,5);

    clilen = sizeof(cli_addr);
    newsockfd = accept(*sockfd, 
                (struct sockaddr *) &cli_addr, 
                &clilen);
    if (newsockfd < 0) 
        error("ERROR on accept");

    return newsockfd;
}

unsigned char* get_message(int socket, unsigned int size){
    int n;
    unsigned int acumulator = 0;
    unsigned char* buf = (unsigned char*)malloc(size*(sizeof(unsigned char)));
    while (acumulator < size){
        n = read( socket, &(buf[acumulator]), size - acumulator );
        acumulator += n;
        if (n < 0) 
            error("ERROR writing to socket");
    }
    return buf;
}

unsigned int decode_size(unsigned char *size){
    unsigned int pack_size = ((int)size[3] << (8*3)) + ((int)size[2] << (8*2)) + ((int)size[1] << (8*1)) + ((int)size[0] << (8*0));
    free(size);
    return pack_size;
}

vector<uchar> decode_frame(unsigned char *frame, unsigned int size){
    vector<uchar> v;
    for (unsigned int i=0; i<size; i++){
        v.push_back(frame[i]);
    }
    free(frame);
    return v;
}

void request_frame(int socket){
    char ack = (char) 0;
    write(socket,&ack,1);
}

void get_frame(int socket){
    Mat frame;
    unsigned int pack_size;
    vector<uchar> vFrame;
    while(true){
        // request_frame(socket);
        pack_size = decode_size(get_message(socket, 4));
        vFrame = decode_frame(get_message(socket, pack_size), pack_size);
        frame = imdecode(vFrame, CV_LOAD_IMAGE_COLOR);
        imshow("result", frame);
        if ( waitKey( 10 ) >= 0 ){
            break;
        }   
    }
    // unsigned char *pack_size_buffer =  get_message(socket, 4);
    // printf("%d %d %d %d\n", (int)pack_size_buffer[0], (int)pack_size_buffer[1], (int)pack_size_buffer[2], (int)pack_size_buffer[3]);
}

int main(int argc, char *argv[]) {
    int socket, *sockfd;
    sockfd = (int*) malloc(sizeof(int));
    cvNamedWindow( "result", 1 );
    if (argc < 2) {
        fprintf(stderr,"ERROR, no port provided\n");
        exit(1);
    }
    socket = create_server(atoi(argv[1]), sockfd);
    get_frame(socket);
    close(socket);
    close(*sockfd);
    free(sockfd);
    return 0; 
}