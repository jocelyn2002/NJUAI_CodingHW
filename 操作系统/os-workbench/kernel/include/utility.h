int mod(int i, int b);  // 取模
int dprintf(const char * fmt,...); // debug用printf

// debug用assert
#ifdef DHDEBUG
    #define dassert(cond) assert(cond)
#else
    #define dassert(cond) ((void)0)
#endif