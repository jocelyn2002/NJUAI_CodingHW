#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <sys/mman.h>
#include <string.h>
#include <wchar.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>
#include <math.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <malloc.h>


// DIR_ENTRY的DIR_Attr
#define  ATTR_READ_ONLY 0x01
#define  ATTR_HIDDEN 0x02
#define  ATTR_SYSTEM 0x04
#define  ATTR_VOLUME_ID 0x08
#define  ATTR_DIRECTORY 0x10
#define  ATTR_ARCHIVE 0x20
#define  ATTR_LONG_NAME  (ATTR_READ_ONLY|ATTR_HIDDEN|ATTR_SYSTEM|ATTR_VOLUME_ID)
// 硬编码：sector 大小是 512, 每个 cluster 有 8 个 sectors, 总大小64mb
#define BytsPerSec 512
#define SecPerClus 8
#define CLUSTERSZ (BytsPerSec*SecPerClus)
#define NCLUSTERS 16384*2


struct FAT32_BPB {
    uint8_t        BS_jmpBoot[3];
    uint8_t        BS_OEMName[8];
    uint16_t    BPB_BytsPerSec; // 每个sector的byte数
    uint8_t     BPB_SecPerClus; // 每个cluster的sector数
    uint16_t    BPB_RsvdSecCnt; // reserved region中的reserved sector数
    uint8_t     BPB_NumFATs;    // FAT的总数，1或者2
    uint16_t    BPB_RootEntCnt; // 全0
    uint16_t    BPB_TotSec16;   // 全0
    uint8_t     BPB_Media;
    uint16_t    BPB_FATSz16;    // 全0
    uint16_t    BPB_SecPerTrk;  
    uint16_t    BPB_NumHeaders;
    uint32_t    BPB_HiddSec;
    uint32_t    BPB_TotSec32;   // 总sector数
    uint32_t    BPB_FATSz32;    // 一个FAT的sector数
    uint16_t    BPB_ExtFlags;
    uint16_t    BPB_FSVer;
    uint32_t    BPB_RootClus;   // root cluster的cluster号，2或更大
    uint16_t    BPB_FSInfo;     // FSInfo的sector号，通常为1
    uint16_t    BPB_BkBootSec;  // BPB备份的sector号，通常是6
    uint8_t     BPB_Reserved[12];
    uint8_t     BS_DrvNum;
    uint8_t     BS_Reserved1;
    uint8_t     BS_BootSig;
    uint32_t    BS_VollD;
    uint8_t     BS_VolLab[11];
    uint8_t        BS_FilSysType[8];// 字符串"FAT32"
    uint8_t     padding1[420];
    uint16_t    Signature_word;// 0x55和0xAA
    // 如果sector还有空余，则全部为0
}__attribute__((packed));
struct FAT32_FSInfo {
    uint32_t    FSI_LeadSig;        // 用于验证，应该为0x41615252
    uint8_t     FSI_Reserved1[480]; // 全0
    uint32_t    FSI_StrucSig;       // 用于验证，应该为0x61417272
    uint32_t    FSI_Free_Count;     // 最后一个free cluster号
    uint32_t    FSI_Nxt_Free;       // 第一块free cluster号
    uint8_t     FSI_Reserved2[12];  // 全0
    uint32_t    FSI_TrailSig;       // 用于验证，应该为0xAA550000
}__attribute__((packed));
struct FAT32_DIR_Entry {
    uint8_t        DIR_Name[11];   // 全大写文件短名，或subdirectory名
    uint8_t     DIR_Attr;       // 文件读写权限等类型
    uint8_t     DIR_NTRes;      // 全0
    uint8_t     DIR_CrtTimeTenth;// 创建时间，十分之一秒，0-199
    uint16_t    DIR_CrtTime;    // 创建时间，2秒
    uint16_t    DIR_CrtDate;    // 创建日期
    uint16_t    DIR_LstAccDate; // 最后访问日期
    uint16_t    DIR_FstClusHI ; // 文件首个cluster号的高16位
    uint16_t    DIR_WrtTime;    // 最后修改时间，2秒
    uint16_t    DIR_WrtDate;    // 最后修改日期
    uint16_t    DIR_FstClusLO;  // 文件首个cluster号的低16位
    uint32_t    DIR_FileSize;   // 文件大小
}__attribute__((packed));
struct FAT32_LongName_Entry {
    uint8_t     LDIR_Ord; // 序号， 如果是最后一个要用0x40遮罩
    uint16_t    LDIR_Name1[5]; // 1-5号字符
    uint8_t     LDIR_Attr; //必须为ATTR_LONG_NAME
    uint8_t     LDIR_Type; // 全0
    uint8_t     LDIR_Chksum; //校验码
    uint16_t    LDIR_Name2[6]; // 6-11号字符
    uint16_t    LDIR_FstClusLO; // 全0
    uint16_t    LDIR_Name3[2]; // 12-13字符
}__attribute__((packed));
struct Sector {
    uint8_t value[BytsPerSec];
}__attribute__((packed));
struct Cluster {
    struct Sector sectors[SecPerClus];
}__attribute__((packed));
struct FAT32_Volumn {
    struct Cluster clusters[NCLUSTERS];
}__attribute__((packed));

struct BMP_Header {
    uint16_t bfType;
    uint32_t bfSize;
    uint32_t reserved;
    uint32_t bfOffBits; // 从文件头到实际图像数据之间的字节偏移量
}__attribute__((packed));
struct BMP_Info {
    uint32_t biSize;
    uint32_t biwidth;
    uint32_t biHeight;
    uint16_t biPlanes;
    uint16_t biBitCount;
    uint32_t biCompression;
    uint32_t biSizeImage;
    uint32_t biXPelsPerMeter;
    uint32_t biYpelsPerMeter;
    uint32_t biClrUsed;
    uint32_t biClrImportant;
}__attribute__((packed));


// #define DHDEBUG
#define RGB 6000000 // gcx亲测有效40


int32_t total_clusters;
struct FAT32_Volumn * fat;
uint8_t *bit_map;
int32_t derivation;

#ifdef DHDEBUG
double max_l1;
double lm1;
#endif

// void fuck(int32_t i) {
//     printf("fuck-%d\n",i);
// }
void get_name(struct FAT32_LongName_Entry * entry,char * name) {
    char tmpname[64];
    memset(tmpname,0,64);
    strcpy(tmpname,name);
    memset(name,0,64);
    char * cur = name;
    for (int32_t i=0;i<5;i++){
        if (entry->LDIR_Name1[i]!=0x0000 && entry->LDIR_Name1[i]!=0xffff){
            *cur = (uint8_t)entry->LDIR_Name1[i];
            cur++;
        }
    }
    for (int32_t i=0;i<6;i++){
        if (entry->LDIR_Name2[i]!=0x0000 && entry->LDIR_Name2[i]!=0xffff){
            *cur = (uint8_t)entry->LDIR_Name2[i];
            cur++;
        }
    }
    for (int32_t i=0;i<2;i++){
        if (entry->LDIR_Name3[i]!=0x0000 && entry->LDIR_Name3[i]!=0xffff){
            *cur = (uint8_t)entry->LDIR_Name3[i];
            cur++;
        }
    }
    // printf("fuck\n");
    strcat(name,tmpname);
}
int32_t ascii_check(char * name) {
    for (char * cur = name;*cur!='\0';cur++)
        if (!(0<=*cur && *cur<=127))
            return 0;
    return 1;
}

int32_t L2(uint8_t * buf1, uint8_t * buf2, uint8_t * buf3, int32_t line_bytes, int32_t buf2_bytes) {
    // 使用MSE
    int32_t sums = 0;
    for (int32_t i=0;i<buf2_bytes;i++) {
        int32_t ab = abs(buf1[i]-buf2[i]); 
        sums+=ab*ab;
    }
    for (int32_t i=0;i<line_bytes-buf2_bytes;i++) {
        int32_t ab = abs(buf1[i+buf2_bytes]-buf3[i]);
        sums+=ab*ab;
    }
    return sums;
}

int32_t get_next_cluster(int32_t cluster,int32_t width, int32_t byte_remain) {
    uint8_t * buf1 = (uint8_t*)(((uint8_t*)&fat->clusters[cluster+1])-byte_remain-width);
    uint8_t * buf2 = (uint8_t*)(((uint8_t*)&fat->clusters[cluster+1])-byte_remain);
    uint8_t * buf3 = (uint8_t *)&fat->clusters[cluster+1];
    
    int32_t this_l1 = L2(buf1,buf2,buf3,width,byte_remain);
    
    int32_t ret;

    if (this_l1 < RGB) {
#ifdef DHDEBUG
        if (this_l1>lm1)
            lm1=this_l1;
#endif
        bit_map[cluster+1] = 1;
        ret = cluster+1;
        bit_map[ret] = 1;
    }
    else {
        int32_t min_l1=0xfffffff;
        int32_t min_cluster=2;

        for (int32_t i=2;i<total_clusters;i++) {
            if (bit_map[i]==1) continue;
            int32_t this_l1 = L2(buf1,buf2,(uint8_t *)&fat->clusters[i],width,byte_remain);

            if (this_l1<min_l1) {
                min_l1=this_l1;
                min_cluster=i;
            }
        }
        ret = min_cluster;
        if (min_l1<2000000) bit_map[min_cluster] = 1;
    }
    return ret;
}
void get_sha1sum(struct FAT32_DIR_Entry * entry, char * buf, char * file_name) {
    // 本地34可以
    int32_t cluster = ( (uint32_t)(entry->DIR_FstClusHI << 16)) | (uint32_t)(entry->DIR_FstClusLO);
    // 首个cluster直接标1
    bit_map[cluster] = 1;

    int32_t original_cluster = cluster;
    int32_t filesz = entry->DIR_FileSize;
    
    struct BMP_Header * bh = (struct BMP_Header *)&fat->clusters[cluster];
    int32_t offset = bh->bfOffBits;
    struct BMP_Info * bi = (struct BMP_Info *)(bh+1);
    int32_t width = bi->biwidth;
    width = 3*width;
    while (width % 4) width++;
    int32_t height = bi->biHeight;
    assert(width*height+offset==filesz);

    char name[128] = "/tmp/";
    strcat(name,file_name);
    FILE *fp1 = fopen(name, "w");
    int32_t original_filesz = filesz;
    int32_t byte_remain = (CLUSTERSZ-offset)%width;

    fwrite((void *)&fat->clusters[cluster],1,CLUSTERSZ,fp1);
    filesz -= CLUSTERSZ;  
    

#ifdef DHDEBUG
    lm1=0;
#endif

    while (1) {
        cluster = get_next_cluster(cluster,width,byte_remain);
        if (filesz<=CLUSTERSZ) {
            fwrite((void *)&fat->clusters[cluster],1,filesz,fp1);
            fclose(fp1);
            goto Done;
        }
        else{
            fwrite((void *)&fat->clusters[cluster],1,CLUSTERSZ,fp1);
            filesz-=CLUSTERSZ;
            byte_remain = (CLUSTERSZ-(width-byte_remain))%width;
        }
    }
    
    
    fclose(fp1);
    Done:

    memset(buf,0,128);
    char command[128] = "sha1sum ";
    strcat(command,name);
    FILE * fp = popen(command, "r");
    fscanf(fp, "%s", buf);
    pclose(fp);
}

struct FAT32_Volumn * init(char * filename) {
    int32_t fd = open(filename,O_RDWR);
    struct stat * buf = malloc(sizeof(struct stat));
    stat(filename, buf);
    struct FAT32_BPB * bpb = mmap(NULL, buf->st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

    uint8_t * DataAddr = ((uint8_t *)((uint8_t *)bpb  + bpb->BPB_RsvdSecCnt * bpb->BPB_BytsPerSec) + (bpb->BPB_FATSz32 * bpb->BPB_BytsPerSec) * bpb->BPB_NumFATs);
    uint8_t * addBound = (uint8_t *)bpb + buf->st_size;
    total_clusters = (addBound - DataAddr)/CLUSTERSZ + 2;
    bit_map = malloc(total_clusters);
    memset(bit_map,0,total_clusters);

    struct FAT32_Volumn *fat = (struct FAT32_Volumn*)((intptr_t)DataAddr - 2*CLUSTERSZ);
    struct Sector* tmp = &fat->clusters[2].sectors[0];
    int32_t aa = *(int32_t*)tmp;

#ifdef DHDEBUG
    max_l1=0;
#endif
    
    return fat;
}

void get_long() {
#ifdef DHDEBUG
    int32_t cc=0;
    int32_t dd=0;
#endif
    
    for (int32_t j=2;j<=total_clusters;j++){
        struct FAT32_LongName_Entry * entry = (struct FAT32_LongName_Entry *)&fat->clusters[j];
        
        for (int32_t i=0;i<128;i++,entry++){
            // 检测到long name起始
            if(entry->LDIR_Attr==ATTR_LONG_NAME && entry->LDIR_Type == 0 && entry->LDIR_FstClusLO==0 && ((entry->LDIR_Ord) & 0x40)!=0){
                // 目录项排除
                bit_map[j] = 1;

                char file_name[64];
                memset(file_name,0,64);
                int32_t dirs = entry->LDIR_Ord ^ 0x40;
                if (dirs>5) continue;
                for (int32_t j=dirs;j>=1;j--,i++,entry++) {
                    get_name(entry,&file_name[0]);
                }
                
                if (ascii_check(file_name)!=0) {
                    
                    char buf[128];
                    get_sha1sum((struct FAT32_DIR_Entry *)entry,&buf[0],file_name);
                
                #ifdef DHDEBUG    
                    char buf1[128];
                    char filename[128];
                    memset(filename,0,128);
                    strcpy(filename,"sha1sum /mnt/DCIM/");
                    strcat(filename,file_name);
                    memset(buf1,0,128);
                    FILE * fp = popen((char *) &filename[0], "r");
                    fscanf(fp, "%s", buf1);
                    pclose(fp);
                    if (strcmp(buf,buf1)==0){
                        if (lm1>max_l1)
                            max_l1=lm1;
                        dd++;
                    }
                #endif
                    printf("%s  %s\n",buf,file_name);
                    fflush(stdout);
                }
                #ifdef DHDEBUG
                cc ++;
                #endif
            }
        }
        
    }

#ifdef DHDEBUG
    printf("total long name: %d\n",cc);
    printf("accuracy %lf\n",(double)dd/cc);
#endif
}


// 只恢复名字
void get_long32(){
    for (int32_t j=2;j<=total_clusters;j++){
        struct FAT32_LongName_Entry * entry = (struct FAT32_LongName_Entry *)&fat->clusters[j];
        for (int32_t i=0;i<128;i++,entry++){
            // 检测到long name起始
            if(entry->LDIR_Attr==ATTR_LONG_NAME && entry->LDIR_Type == 0 && entry->LDIR_FstClusLO==0 && ((entry->LDIR_Ord) & 0x40)!=0){
                char file_name[64];
                memset(file_name,0,64);
                int32_t dirs = entry->LDIR_Ord ^ 0x40;
                if (dirs>5) continue;
                for (int32_t j=dirs;j>=1;j--,i++,entry++) {
                    get_name(entry,&file_name[0]);
                }
                if (ascii_check(file_name)!=0) {
                    
                    uint8_t buf[128];
                    printf("e0827a916543e8e442611016ad6f9e97a864a929  %s\n",file_name);
                }
            }
        }
    }
}
int main(int32_t argc, char *argv[]) {
#ifdef DHDEBUG
    struct timeval tv;
    gettimeofday(&tv, NULL);
    long start = tv.tv_sec*1000000 + tv.tv_usec;
#endif
    fat = init(argv[1]);
// #ifdef __x86_64__
    get_long32();
    get_long();
    
// #else
    // get_long32();
// #endif
#ifdef DHDEBUG
    printf("maxl1: %f\n",max_l1);
    gettimeofday(&tv, NULL);
    double time_total = (tv.tv_sec*1000000 + tv.tv_usec - start)/1000000.0;
    printf("time: %.3f\n",time_total);

    int32_t sum=0;
    for(int32_t i=2;i<total_clusters;i++)
        if (bit_map[i]==0)
            sum++;
    printf("total:%d write:%d\n",total_clusters,total_clusters-2-sum);
#endif
    return 0;
}