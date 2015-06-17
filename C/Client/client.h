void error(const char *msg);

void connect2server(int portno, char* hostname, int *sockfd);

int wait_request(int sockfd, float time_out);

void stream_video(int sockfd);