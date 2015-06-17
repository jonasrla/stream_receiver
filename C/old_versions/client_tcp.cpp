#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <unistd.h>
#include "opencv2/highgui/highgui.hpp"
#include <iostream>

using namespace std;
using namespace cv;

void error(const char *msg)
{
    perror(msg);
    exit(0);
}

void connect2server(int portno, char* hostname, int *sockfd){
    struct sockaddr_in serv_addr;
    struct hostent *server;

    *sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");

    server = gethostbyname(hostname);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }

    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
        (char *)&serv_addr.sin_addr.s_addr,
        server->h_length);
    serv_addr.sin_port = htons(portno);

    if (connect(*sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
        error("ERROR connecting");
}

void stream_video(int sockfd){
    CvCapture* capture = 0;
    IplImage* iplImg = NULL;
    int n;
    unsigned int pack_size;
    vector<uchar> buf;

    capture = cvCaptureFromCAM( CV_CAP_ANY );
    if(!capture) cout << "Capture from CAM didn't work" << endl;
    
    cvNamedWindow( "result", 1 );

    while (true){
        iplImg = cvQueryFrame( capture );
        imencode(".jpg",(Mat)iplImg,buf);
        pack_size = buf.size();
        // printf("%d\n", pack_size);
        n = write(sockfd,&pack_size,sizeof(pack_size));
        for (vector<uchar>::iterator it = buf.begin(); it != buf.end(); ++it){
            n = write(sockfd,&(*it),sizeof(*it));
            if (n < 0) 
                 error("ERROR writing to socket");
        }
        
        
        if ( waitKey( 10 ) >= 0 ){
            cvReleaseCapture( &capture );
            break;
        }
    }
}

int main(int argc, char *argv[])
{
    int *sockfd, n;
    sockfd = (int *) malloc(sizeof(int));
    if (argc < 3) {
       fprintf(stderr,"usage %s hostname port\n", argv[0]);
       exit(0);
    }
    connect2server(atoi(argv[2]), argv[1], sockfd);

    stream_video(*sockfd);

    // n = write(*sockfd,buffer,strlen(buffer));
    // if (n < 0) 
    //      error("ERROR writing to socket");
    // bzero(buffer,256);
    // n = read(*sockfd,buffer,255);
    // if (n < 0) 
    //      error("ERROR reading from socket");
    // printf("%s\n",buffer);
    close(*sockfd);
    free(sockfd);
    return 0;
}