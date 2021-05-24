#include<iostream>
#include<string>
#include<vector>
#include<fstream>
#include<sstream>
#include<algorithm>
using namespace std;

struct transition {
    string old_state;
    vector<char> old_symbols;
    vector<char> new_symbols;
    vector<char> directions;
    string new_state;
};
struct TM {
    // 集合
    vector<string> Q,F;
    vector<char> S,G;
    string q0;
    char B;
    int N;
    vector<struct transition> transitions;

    // ID
    string state;
    vector<vector<char>> tapes;
    vector<int> start,head; // start表示第一个非空字符（tapes[0]）的index，用负数表示。head表示读写头的位置，即tapes[i]中的i
};


bool verbose = false;


bool add_elements(string line,vector<string> &set) {
    int n = line.find_last_of("}");
    if(n == string::npos) return false;
    line.erase(n,line.size()-n+1);
    
    n = line.find_first_of("{");
    if(n == string::npos) return false;
    line.erase(0,n+1);

    // TODO：空集处理
    n = line.find_first_of(",");
    while (n != string::npos) {
        string tmp_string = line.substr(0,n);
        set.push_back(tmp_string);
        line.erase(0,n+1);
        n = line.find_first_of(",");
    }
    set.push_back(line);
    return true;
}
bool add_elements(string line,vector<char> &set) {
    int n = line.find_last_of("}");
    if(n == string::npos) return false;
    line.erase(n,line.size()-n+1);
    
    n = line.find_first_of("{");
    if(n == string::npos) return false;
    line.erase(0,n+1);

    // TODO：空集处理
    n = line.find_first_of(",");
    while (n != string::npos) {
        string tmp_string = line.substr(0,n);
        char tmp_str = tmp_string[0];
        set.push_back(tmp_str);
        line.erase(0,n+1);
        n = line.find_first_of(",");
    }
    char tmp_str = line[0];
    set.push_back(tmp_str);
    return true;
}
bool in(char c, string in_string) {
    size_t a = in_string.find(c);
    if (a==string::npos)
        return false;
    return true;
}
bool in(string s,string in_string) {
    for(int i=0;i<s.size();i++) {
        size_t a = in_string.find(s[i]);
        if (a==string::npos)
            return false;
    }
    return true;
}

// 打印图灵机的当前状态
void printID(struct TM *tm) {
    for (int i=0;i<tm->N;i++) {
        // Index行
        cout <<"Index"<< i <<" :";
        int id=tm->start[i];
        for (int j=0;j<tm->tapes[i].size()-1;j++) {
            cout << " " << (id>0?id:-id);
            id += 1;
        }
        cout << endl;
        // Tape行
        cout <<"Tape"<< i <<"  :";
        id=tm->start[i];
        for (int j=0;j<tm->tapes[i].size()-1;j++) {
            cout << " " << tm->tapes[i][j];
            int tmp_int = id;
            while(tmp_int/10) {
                cout << " ";
                tmp_int /= 10;
            }
            id += 1;
        }
        cout << endl;
        // Head行
        cout <<"Head"<< i <<"  :";
        id=tm->start[i];
        for (int j=0;j<tm->tapes[i].size()-1;j++) {
            if (j==tm->head[i])
                cout << " ^";
            else
                cout << "  ";
            int tmp_int = id;
            while(tmp_int/10) {
                cout << " ";
                tmp_int /= 10;
            }
            id += 1;
        }
        cout << endl;
    }
    cout << "State  : " << tm->state << endl;
    cout <<"---------------------------------------------"<<endl;
}
// 打印一条转移函数
void printTransition(struct transition t) {
    cerr << "(" << t.old_state << " ";
    for (int i=0;i<t.old_symbols.size();i++) cerr << t.old_symbols[i];
    cerr << " ";
    for (int i=0;i<t.new_symbols.size();i++) cerr << t.new_symbols[i];
    cerr << " ";
    for (int i=0;i<t.directions.size();i++) cerr << t.directions[i];
    cerr << " ";
    cerr << t.new_state << ")";
}
// 打印图灵机的定义
void printTM(struct TM *tm) {
    int i;
    cerr << "TM = {Q, S, G, q0, B, N, T}" <<endl;
    // 各种集合
    cerr << "Q = {";
    for (i=0;i<tm->Q.size()-1;i++)
        cerr << tm->Q[i] << ", ";
    cerr << tm->Q[i] << "}" << endl;

    cerr << "S = {";
    for (i=0;i<tm->S.size()-1;i++)
        cerr << tm->S[i] << ", ";
    cerr <<tm->S[i]<< "}" << endl;
    
    cerr << "G = {";
    for (i=0;i<tm->G.size()-1;i++)
        cerr << tm->G[i] << ", ";
    cerr << tm->G[i] <<"}" << endl;

    cerr << "q0 = " << tm->q0 << endl;
    cerr << "B = " << tm->B << endl;
    cerr << "N = " << tm->N << endl;

    cerr << "T = {";
    for (i=0;i<tm->transitions.size()-1;i++) {
        printTransition(tm->transitions[i]);
        cerr << ", ";
    }
    printTransition(tm->transitions[i]);
    cerr << "}" << endl;
}

// 检查图灵机是否合法
bool checkTM(struct TM *tm) {
    // 检查状态集Q
    string Q_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_";
    for (int i=0;i<tm->Q.size();i++){
        if (!in(tm->Q[i],Q_characters)){
            if (verbose)
                cerr << "Invalid StateName: " << tm->Q[i] << endl;
            return false;
        }
    }
    // 检查输入集S
    string S_characters;
    for (char i=33;i<=126;i++)
        S_characters.append(1,i);
    string stop_list = ",;{}*_";
    for (int i=0;i<stop_list.size();i++) {
        size_t a = S_characters.find(stop_list[i]);
        S_characters.erase(a,1);
    }
    for (int i=0;i<tm->S.size();i++){
        if (!in(tm->S[i],S_characters)){
            if (verbose)
                cerr << "Invalid InputSymbolName: " << tm->S[i] << endl;
            return false;
        }
    }
    // 检查纸带集G
    string G_characters = S_characters;
    G_characters.append(1,'_');
    for (int i=0;i<tm->G.size();i++){
        if (!in(tm->G[i],G_characters)){
            if (verbose)
                cerr << "Invalid TapeSymbolName: " << tm->G[i] << endl;
            return false;
        }
    }
    // 检查初始状态
    if (find(tm->Q.begin(), tm->Q.end(), tm->q0) == tm->Q.end() ){
        if(verbose)
            cerr << "Invalid StartState: " << tm->q0 << endl;
        return false;
    }
    // 检查空白符号
    if (find(tm->G.begin(), tm->G.end(), tm->B) == tm->G.end() ){
        if(verbose)
            cerr << "Invalid BlankSymbol: " << tm->B << endl;
        return false;
    }
    // 检查终止状态集
    for (int i=0;i<tm->F.size();i++) {
        if (find(tm->Q.begin(), tm->Q.end(), tm->F[i]) == tm->Q.end() ){
            if(verbose)
                cerr << "Invalid FinalState: " << tm->F[i] << endl;
            return false;
        }
    }
    // 检查转移函数
    for (int i=0;i<tm->transitions.size();i++) {
        struct transition *tmp = &tm->transitions[i];
        // 初始状态、终止状态
        if (find(tm->Q.begin(), tm->Q.end(), tmp->old_state) == tm->Q.end() ){
            if(verbose){
                cerr << "Invalid Transition(old state): ";
                printTransition(*tmp);
                cerr<<endl;
            }
            return false;
        }
        if (find(tm->Q.begin(), tm->Q.end(), tmp->new_state) == tm->Q.end() ){
            if(verbose){
                cerr << "Invalid Transition(new state): ";
                printTransition(*tmp);
                cerr<<endl;
            }
            return false;
        }
        // 旧符号、新符号
        for (int j=0;j<tmp->old_symbols.size();j++) {
            if (find(tm->G.begin(), tm->G.end(), tmp->old_symbols[j]) == tm->G.end() ){
                if(verbose){
                    cerr << "Invalid Transition(old symbols): ";
                    printTransition(*tmp);
                    cerr << endl;
                }
                return false;
            }
        }
        for (int j=0;j<tmp->new_symbols.size();j++) {
            if (find(tm->G.begin(), tm->G.end(), tmp->new_symbols[j]) == tm->G.end() ) {
                if(verbose){
                    cerr << "Invalid Transition(new symbols): ";
                    printTransition(*tmp);
                    cerr << endl;
                }
                return false;
            }
        }
        // 方向
        for (int j=0;j<tmp->directions.size();j++) {
            if (!in(tmp->directions[j],"rl*")){
                if(verbose){
                    cerr << "Invalid Transition(direction): ";
                    printTransition(*tmp);
                    cerr << endl;
                }
                return false;
            }
        }
        // 重复转移函数
        for (int j=0;j<i;j++) {
            if (tm->transitions[j].old_state==tmp->old_state && tm->transitions[j].old_symbols==tmp->old_symbols) {
                if(verbose){
                    cerr << "Multi Transition: ";
                    printTransition(*tmp);
                    cerr << endl;
                }
                return false;
            }
        }
    }
    
    return true;
}
// 根据输入纸袋初始化图灵机
bool initTM(struct TM *tm,string input) {
    // 状态
    tm->state = tm->q0;
    // 构建纸带与读写头
    for (int i=0;i<tm->N;i++){
        tm->tapes.push_back(*new(vector<char>));
        tm->tapes[i].push_back(tm->B);
        tm->tapes[i].push_back(tm->B);
        tm->start.push_back(0);
        tm->head.push_back(0);
    }
    // 输入串
    if (input != ""){
        tm->tapes[0].pop_back();
        for (int i=0;i<input.length();i++) {
            if (find(tm->S.begin(),tm->S.end(),input[i])==tm->S.end()) {
                if (verbose) {
                    cerr << "Input: " << input << endl;
                    cerr << "==================== ERR ====================" << endl;
                    cerr << "error: '"<<input[i]<<"' was not declared in the set of input symbols"<<endl;
                    cerr << "Input: " << input << endl;
                    cerr << "       ";
                    for (int j=0;j<i;j++) cerr<<" ";
                    cerr << "^" << endl;
                    cerr << "==================== END ====================" << endl;
                    return false;
                }
                else{
                    cerr << "illegal input" << endl;
                    return false;
                }   
            }
            tm->tapes[0].insert(tm->tapes[0].end()-1,input[i]);
        }
    }
    if (verbose) {
        cout << "Input: " << input << endl;
        cout << "==================== RUN ====================" << endl;
    }
    return true;
}
// 从.tm文件构建图灵机，并验证是否合法
struct TM *constructTM(string path, string input) {
    ifstream file_in(path);
    if (!file_in) {
        if (verbose)
            cerr << "Invalid TM Filename: " << path <<endl;
        return nullptr;
    }

    TM *ret = new(struct TM);
    string line;
    while (getline(file_in,line)) {
        // 跳过空行
        if (line.size()==0 || line[0]==';') continue;
        
        // 定义集合
        if (line[0] == '#') {
            switch (line[1]) {
                case 'Q':{
                    if (line.substr(0,6)!="#Q = {" || !add_elements(line,ret->Q)) goto dd;
                    break;
                }
                case 'S':{
                    if (line.substr(0,6)!="#S = {" || !add_elements(line,ret->S)) goto dd;
                    break;
                }
                case 'G':{
                    if (line.substr(0,6)!="#G = {" || !add_elements(line,ret->G)) goto dd;
                    break;
                }
                case 'q':{
                    if (line.substr(0,6)!="#q0 = ") goto dd;
                    ret->q0 = line.substr(6,line.size()-6);
                    break;
                }
                case 'B':{
                    if (line.substr(0,5)!="#B = ") goto dd;
                    ret->B = line[5];
                    break;
                }
                case 'F':{
                    if (line.substr(0,6)!="#F = {" || !add_elements(line,ret->F)) goto dd;
                    break;
                }
                case 'N':{
                    if (line.substr(0,5)!="#N = ") goto dd;
                    istringstream ss(line.substr(5,line.size()-5));
                    ss >> ret->N;
                    break;
                }
                default:
                dd:
                    if (verbose)
                        cerr << "Invalid TM Discription: "<< line << endl;
                    cerr << "syntax error" << endl;
                    return nullptr;
            }
        }
        // 定义转移
        else {
            istringstream ss(line);
            string symbols;
            struct transition *tmp_transition = new(struct transition);
            
            ss >> tmp_transition->old_state;
            ss >> symbols;
            for (int i=0;i<ret->N;i++) {tmp_transition->old_symbols.push_back(symbols[i]);}
            ss >> symbols;
            for (int i=0;i<ret->N;i++) tmp_transition->new_symbols.push_back(symbols[i]);
            ss >> symbols;
            for (int i=0;i<ret->N;i++) tmp_transition->directions.push_back(symbols[i]);
            ss >> tmp_transition->new_state;

            ret->transitions.push_back(*tmp_transition);
        }
    }
    
    if (!checkTM(ret)){
        cerr << "syntax error" << endl;
        return nullptr;
    }
    if (!initTM(ret,input)) return nullptr;

    return ret;
}

// 图灵机运行一步，如果存在转移则返回true，如果停机则返回false
bool step(struct TM *tm) {
    bool not_halting = false;
    // 寻找是否存在转移
    struct transition *trans;
    for (int i=0;i<tm->transitions.size();i++) {
        struct transition *tmp = &tm->transitions[i];
        if (tmp->old_state != tm->state) goto CTN;
        for (int j=0;j<tm->N;j++) {
            if (tmp->old_symbols[j] != tm->tapes[j][tm->head[j]]) goto CTN;
        }

        not_halting = true;
        trans = tmp;
        break;

        CTN: continue;
    }

    if (not_halting==false) return false;
    
    // 真的开始转移啦
    // printTransition(*trans);
    tm->state = trans->new_state;
    for (int i=0;i<tm->N;i++) {
        tm->tapes[i][tm->head[i]] = trans->new_symbols[i];
        switch (trans->directions[i]) {
            case '*':{
                break;
            }
            case 'l': {
                tm->head[i] -= 1;
                if (tm->head[i]==-1) {
                    tm->head[i] += 1;
                    tm->start[i] -= 1;
                    tm->tapes[i].insert(tm->tapes[i].begin(),tm->B);
                }
                // 删除右边多余Blank
                while (tm->tapes[i].size()-2 > tm->head[i] && tm->tapes[i][tm->tapes[i].size()-2]==tm->B)
                    tm->tapes[i].pop_back();
                // 删除左边多余Blank
                while (tm->head[i] > 0 && tm->tapes[i][0]==tm->B) {
                    tm->tapes[i].erase(tm->tapes[i].begin());
                    tm->start[i] += 1;
                    tm->head[i] -= 1;
                }
                break;
            }
            case 'r': {
                tm->head[i] += 1;
                if (tm->head[i]==tm->tapes[i].size()-1)
                    tm->tapes[i].push_back(tm->B);
                // 删除右边多余Blank
                while (tm->tapes[i].size()-2 > tm->head[i] && tm->tapes[i][tm->tapes[i].size()-2]==tm->B)
                    tm->tapes[i].pop_back();
                // 删除左边多余Blank
                while (tm->head[i] > 0 && tm->tapes[i][0]==tm->B) {
                    tm->tapes[i].erase(tm->tapes[i].begin());
                    tm->start[i] += 1;
                    tm->head[i] -= 1;
                }
                break;
            }
            default: cerr << "Invalid Direction" << endl;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    int argid = 1;
    string s1 = argv[argid];
    if (s1=="-h" || s1=="--help"){
        cout << "usage: turing [-v|--verbose] [-h|--help] <tm> <input>" << endl;
        return 0;
    }
    if (s1=="-v" || s1=="--verbose"){
        verbose = true;
        argid += 1;
    }

    string tm_name = argv[argid];
    string tm_path = "" + tm_name;
    string input_string = argv[argid+1];
    struct TM *tm = constructTM(tm_path,input_string);
    if (tm==nullptr) return -1;
    // 图灵机运行
    bool cont = true;
    int i=0;
    if (verbose) {
        cout << "Step   : " << i++ << endl;
        printID(tm);
    }
    while (cont) {
        cont = step(tm);
        if (verbose && cont) {
            cout << "Step   : " << i++ << endl;
            printID(tm);
        }
    }
    if (verbose) {
        cout << "Result: ";
        for (int j=0;j<tm->tapes[0].size()-1;j++) cout << tm->tapes[0][j];
        cout << endl;
        cout << "==================== END ====================" << endl;
    }
    else {
        for (int j=0;j<tm->tapes[0].size()-1;j++) cout << tm->tapes[0][j];
        cout << endl;
    }
    return 0;
}