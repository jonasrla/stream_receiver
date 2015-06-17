void error(const char *msg);

int create_server(int portno, int *sockfd);

unsigned char* get_message(int socket, unsigned int size);

unsigned int decode_size(unsigned char *size);

void request_frame(int socket);

unsigned char* get_frame(int socket, int* size);