package controllers.Astar;

import core.game.Observation;
import core.game.StateObservation;
import core.player.AbstractPlayer;
import ontology.Types;
import tools.ElapsedCpuTimer;
import tools.Vector2d;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

public class Agent extends AbstractPlayer{
    // 在整局游戏中不变的“常量”
    private double big_number = 100000000; // 一个“甚大之数”，用来表示无穷大
    protected int block_size; // 像素大小
    private ArrayList<Types.ACTIONS> real_actions; // 可以进行的操作
    private Vector2d dp,kkp; // 门的位置，钥匙的初始为止
    private int hole=-1,mushroom=-1,door=-1; // -1表示没有
    // 初始化
    public Agent(StateObservation stateObs, ElapsedCpuTimer elapsedTimer){
        inner_states = new ArrayList<>();
        outer_states = new ArrayList<>();
        block_size = stateObs.getBlockSize();
        current_sto = new STO(stateObs,null,null, 0, 0);
        is_changing_back = false;
        is_changing_forward = false;
        path_to_target = new ArrayList<>();
        real_actions = new ArrayList<>();
        real_actions = stateObs.getAvailableActions();
        int num_of_immovabletypes = stateObs.getImmovablePositions().length;
        switch (num_of_immovabletypes){
            case 2:
                door=1;
                break;
            case 3:
                hole=1;
                door=2;
                break;
            case 4:
                hole=1;
                mushroom=2;
                door=3;
        }
        kkp = new Vector2d(stateObs.getMovablePositions()[0].get(0).position);
        dp = new Vector2d(stateObs.getImmovablePositions()[door].get(0).position);
    }



    // 待调参的系数
    private double c_g=0.1/50; // 已经走过的路程的曼哈顿距离开销
    private double c_Manhattan=0.5/50; // 到达终点的曼哈顿距离的开销
    private double[] c_n={4096,512,256,512,0}; // Avatar碰着的木块们，他们是0，1，2，3，4向可动的时，每一个增加的开销
    private double c_hole= -2048.0; // 表示Avatar所碰着的木块可以在之后被推进洞时的每一个洞的开销
    private double c_noh = -1024.0; // 表示Avatar所碰着的木块周围八格每一个洞的开销
    private double c_score= -4096.0; // 每增加一分减少的开销
    private double c_rand=0; // 随机项（0-9）的系数

    // f = g + h,这个函数是本题的重点
    private double eval(StateObservation stateObs, int depth){
        // 两种极端情况，若已经到达终点返回0，死了返回无穷大
        if (stateObs.getGameWinner()==Types.WINNER.PLAYER_WINS) return 0;
        // 其他结束游戏的情况就是死了
        if (stateObs.isGameOver()) return big_number;

        // 获取玩家位置
        Vector2d ap = new Vector2d(stateObs.getAvatarPosition());
        double total_cost=0; // 总开销


        // g:
        // 已经走过的路程的开销，使用曼哈顿距离
        if (!k_c)
            total_cost += c_g*depth*block_size;


        // h:
        // 1.门、玩家、钥匙的距离开销,使用曼哈顿距离
        double distance_cost=0;
        try {
            Vector2d kp = new Vector2d(stateObs.getMovablePositions()[0].get(0).position);
            distance_cost += Math.abs(ap.x-kp.x)+Math.abs(ap.y-kp.y)+Math.abs(kp.x-dp.x)+Math.abs(kp.y-dp.y);
        } // 拿到钥匙前
        catch(Exception e){
            distance_cost += Math.abs(ap.x-dp.x)+Math.abs(ap.y-dp.y);
        }// 拿到钥匙后
        distance_cost *= c_Manhattan;
        total_cost+=distance_cost;

        // 2.游戏分数奖励开销
        double score_cost = c_score*stateObs.getGameScore();
        total_cost += score_cost;

        // 3.所有木块自由度的开销，推到死角相应开销较大，同时判定不可让木块覆盖钥匙
        double brick_cost = get_brick_cost(stateObs,ap);
        if (brick_cost==-1) {
            return big_number;
        } // 木块推到了钥匙上
        total_cost += brick_cost;


        Random r = new Random();
        double cost_r = r.nextInt(10)*c_rand;
        total_cost+=cost_r;

        return big_number/10+total_cost;
    }

    // 获取木块相关开销
    private int to_int(boolean b){
        if (b) return 1;
        else return 0;
    }
    private boolean is_hole(int x, int y, ArrayList<Vector2d> hp, int x0,int y0){
        double new_x = (x+x0)*block_size;
        double new_y = (y+y0)*block_size;
        System.out.printf("\n待检查洞的坐标为： %f %f\n",new_x,new_y);
        Vector2d opposite = new Vector2d(new_x,new_y);
        return hp.contains(opposite);
    }
    private double get_brick_cost(StateObservation stateObs, Vector2d ap){
        // 获取木块位置
        ArrayList<Vector2d> bp = new ArrayList<>(); // 每一个元素代表一个木块
        for (int i=0; i<=100; i++){
            try{
                Vector2d brick_position = stateObs.getMovablePositions()[1].get(i).position;
                // 当木块处在阿凡达周围的九宫格之内时，把它加入列表
                if (brick_position.dist(ap)<1.5*block_size)
                    bp.add(brick_position); }
            catch(Exception e){ break; }
        } // 一直加到没有木块为止
        // 把木块推到钥匙上是不可允许的，返回负值表示格子推到了箱子上
        if (bp.contains(kkp)){
            return -1;
        }


        // 计算每一种自由度的木块数量
        ArrayList<Observation>[][] grid = stateObs.getObservationGrid();
        int[] n = new int[5];  // 每一个自由度的木块数
        double cost=0;
        for (Vector2d brick: bp){
            // 绘制此木块周围一圈8个点的物体表格
            int[] around = new int[8];
            int x = (int)brick.x/block_size;
            int y = (int)brick.y/block_size;
            // 从最右开始，逆时针遍历一圈（极坐标顺序）,用-1指代空位，查看Types源代码知Avatar为0,其他物体为>0
            try{ around[0]=grid[x+1][y].get(0).category; } catch(Exception e){around[0]=-1;}
            try{ around[1]=grid[x+1][y-1].get(0).category; } catch(Exception e){around[1]=-1;}
            try{ around[2]=grid[x][y-1].get(0).category; } catch(Exception e){around[2]=-1;}
            try{ around[3]=grid[x-1][y-1].get(0).category; } catch(Exception e){around[3]=-1;}
            try{ around[4]=grid[x-1][y].get(0).category; } catch(Exception e){around[4]=-1;}
            try{ around[5]=grid[x-1][y+1].get(0).category; } catch(Exception e){around[5]=-1;}
            try{ around[6]=grid[x][y+1].get(0).category; } catch(Exception e){around[6]=-1;}
            try{ around[7]=grid[x+1][y+1].get(0).category; } catch(Exception e){around[7]=-1;}

            // 找到Avatar位置
            int index_avatar=-1;
            for (int i =0;i<8;i++)
                if (around[i]==0){
                    index_avatar = i;
                    break;
                }
            // 确定Avatar能走到哪些位置
            int[] available_table = new int[8]; // 网上说int数组自动初始化为0，试试看
            for (int j = index_avatar;j <= 7; j++){
                if (around[j]<=0)
                    available_table[j]=1;
                else break;
                if (j==7){
                    for (int j2 = 0; j2 < index_avatar;j2++){
                        if (around[j2]<=0)
                            available_table[j2]=1;
                        else break;
                    }
                }
            }
            for (int j = index_avatar;j >= 0; j--){
                if (around[j]<=0)
                    available_table[j]=1;
                else break;
                if (j==0){
                    for (int j2 = 7; j2 > index_avatar;j2--){
                        if (around[j2]<=0)
                            available_table[j2]=1;
                        else break;
                    }
                }
            }


            // 看一看洞
            if (hole!=-1) {
                ArrayList<Vector2d> hp = new ArrayList<>(); // 每一个元素代表一个洞
                ArrayList<Vector2d> hp8 = new ArrayList<>();
                for (int i = 0; i <= 100; i++) {
                    try {
                        Vector2d hole_position = stateObs.getImmovablePositions()[hole].get(i).position;
                        // 当洞处在木块九宫格之内时
                        if (hole_position.dist(brick) < 1.5 * block_size)
                            hp8.add(hole_position);
                        if (hole_position.dist(brick) < 1.5 * block_size)
                            hp.add(hole_position);
                    } catch (Exception e) {
                        break;
                    }
                } // 一直加到没有洞为止
                int n_of_holes = hp8.size();
                System.out.print("\nAvatar position:");
                System.out.println(stateObs.getAvatarPosition());
                System.out.println(Arrays.toString(available_table));

                int n_of_useful_holes = 0;
                if (is_hole(x, y, hp, -1, 0)) {
                    if (available_table[0] == 1) {
                        System.out.println("哇！可以进左边洞！！");
                        n_of_useful_holes += 1;
                    }
                }
                if (is_hole(x, y, hp, 0, 1)) {
                    if (available_table[2] == 1) {
                        System.out.println("哇！可以进下边洞！！");
                        n_of_useful_holes += 1;
                    }
                }
                if (is_hole(x, y, hp, 1, 0)) {
                    if (available_table[4] == 1) {
                        System.out.println("哇！可以进右边洞！！");
                        n_of_useful_holes += 1;
                    }
                }
                if (is_hole(x, y, hp, 0, -1)) {
                    if (available_table[6] == 1) {
                        System.out.println("哇！可以进上边洞！！");
                        n_of_useful_holes += 1;
                    }
                }

                cost += c_noh*n_of_holes;
                cost += c_hole*n_of_useful_holes;
            }



            // 进不了洞，判断自由度
            int num_available=0;
            num_available= available_table[0]*to_int(around[4]<=0)
                        +available_table[2]*to_int(around[6]<=0)
                        +available_table[4]*to_int(around[0]<=0)
                        +available_table[6]*to_int(around[2]<=0);
            n[num_available]+=1;
        }


        for (int i=0;i<=4;i++)
            cost += c_n[i]*n[i];

//        System.out.println();
//        System.out.println(cost);

        return cost;
    }




    // 以下为基础程序，经过debug可以正常运转，能否成功全看上面的评估函数
    // 游戏中会实时改变的量
    private ArrayList<STO> inner_states; // 后方，不用管了
    private ArrayList<STO> outer_states; // 前线，需要判断的格子
    private STO current_sto; // 表示当前精灵所在节点
    private STO target_sto; // 在切换时，表示目标节点
    private boolean is_changing_back,is_changing_forward,k_c=false; // 在切换时，是否在倒退，是否在前进
    private ArrayList<Types.ACTIONS> path_to_target; // 从根节点到目标节点的路径



    @Override
    public Types.ACTIONS act(StateObservation stateObs, ElapsedCpuTimer elapsedTimer) {
        System.out.println("-----------------");
        System.out.println(inner_states.size());
        System.out.println(outer_states.size());
        // 当在切换分支时，不用管之后的，直接返回切换过程的一步
        if (is_changing_back || is_changing_forward) {
            Types.ACTIONS action = change();
            System.out.println();
            System.out.println(action);
            return action;
        }
//         走完path_to_target后并未到达target，说明先前的探索产生了不可逆转的错误
        else if (!(current_sto.ob.equalPosition(stateObs))){
            System.out.println("不可逆转错误");
            // 尝试用朴素的方法修正错误（把当前节点设为起点，重新来过）
            inner_states.clear();
            outer_states.clear();
            current_sto = new STO(stateObs.copy(),null,null, 0, 0);
            return null;
        }



        // 把当前节点变成内部节点
        if (!inner_states.contains(current_sto))
            inner_states.add(current_sto);
        outer_states.remove(current_sto);


        // 扩张周围4个节点
        int advance_depth = current_sto.depth+1;
        Types.ACTIONS chosen_action=null;
        for (Types.ACTIONS action: real_actions){
            StateObservation stcopy = current_sto.ob.copy();
            stcopy.advance(action);
            // 检查是否没动
            if (stcopy.equalPosition(current_sto.ob)) continue;
            // 检查此节点是否在后方,后方直接不要
            boolean is_inner = false;
            for (STO sto: inner_states){
                if (sto.ob.equalPosition(stcopy)){
                    is_inner = true;
                    break;
                }
            }
            if (is_inner) continue;
            // 计算此节点的价值
            double cost = eval(stcopy,advance_depth);
            // 检查此节点是否已经被包含在前线,然后如果有需要的话并执行相应的换父亲操作
            boolean is_outer = false;
            for (STO sto: outer_states){
                if (sto.ob.equalPosition(stcopy)){
                    is_outer = true;
                    if (cost<sto.cost){
                        is_outer = false;
                        sto.cost = cost;
                        sto.myfather = current_sto;
                        sto.fatheraction = action;
                    }
                    break;
                }
            }
            if (is_outer) continue;
            // 至此，这就是一个新的前线节点
            STO sto1 = new STO(stcopy,current_sto,action,advance_depth,cost);
            System.out.println(action);
            System.out.println(sto1.cost);
//            System.out.println(sto1);
//            System.out.println(sto1.myfather);
            outer_states.add(sto1);
        }


        // 选择前线cost最小的节点,向他迈出一步
        double min_cost = big_number;
        target_sto = null;
//        System.out.println();
//        System.out.println("最优叶子节点，其父亲，当前节点");
        for (STO sto: outer_states){
            if (sto.cost < min_cost){
                target_sto = sto;
                min_cost = sto.cost;
            }
        }
        if (target_sto == null) {
            System.out.println("你gg了弟弟！！！");
            return null;
        }
//        System.out.println(target_sto);
//        System.out.println(target_sto.myfather);
//        System.out.println(current_sto);

        // 新最优节点就在展开处
        if (target_sto.myfather==current_sto){
            chosen_action = target_sto.fatheraction;
            // 看一下新方法是否把地图改了，如果改了地图，则把所有旧的搜索结果清空，重新来
            if (map_changed(target_sto.ob)) {
                inner_states.clear();
                outer_states.clear();
                current_sto = new STO(target_sto.ob,null,null, 0, 0);
            }
            else current_sto = target_sto;
        }
        // 如果很不幸，不在这里
        else{
            is_changing_forward = false;
            is_changing_back = true;
            STO sto_pointer = new STO(null,target_sto,null,0,0);
            // 这里就是为了用个指针，所以别的变量不讲究
            while(sto_pointer.myfather != null){
                path_to_target.add(sto_pointer.myfather.fatheraction);
                sto_pointer = new STO(null,sto_pointer.myfather.myfather,null,0,0);
            }
        }

        // 探索过程最终输出
        System.out.println();
        System.out.println(chosen_action);
        return chosen_action;
    }
    // 切换到前线的新节点。在此提出一个重要假设：所有走过的方法在撤回时，都“没有造成不可逆转的坏影响”
    private Types.ACTIONS change(){
        Types.ACTIONS action = null;
        if (is_changing_back){
            action = get_re(current_sto.fatheraction);
            current_sto = current_sto.myfather;
            if (current_sto.myfather==null){
                is_changing_back=false;
                is_changing_forward=true;
            }
        }
        else if (is_changing_forward){
            action = path_to_target.get(path_to_target.size()-1);
            path_to_target.remove(path_to_target.size()-1);
            if (path_to_target.size()==0) {
                is_changing_forward=false;
                current_sto = target_sto.myfather;
                // 看一下新方法是否把地图改了，如果改了地图，则把所有旧的搜索结果清空，重新来
                if (map_changed(target_sto.ob)) {
                    inner_states.clear();
                    outer_states.clear();
                    current_sto = new STO(target_sto.ob,null,null, 0, 0);
                }
                else current_sto=target_sto;
            }
        }
        return action;

    }
    // 用来返回一个操作的反操作
    private Types.ACTIONS get_re(Types.ACTIONS action){
        switch (action){
            case ACTION_LEFT:
                return Types.ACTIONS.ACTION_RIGHT;
            case ACTION_RIGHT:
                return Types.ACTIONS.ACTION_LEFT;
            case ACTION_DOWN:
                return Types.ACTIONS.ACTION_UP;
            case ACTION_UP:
                return Types.ACTIONS.ACTION_DOWN;
            default:
                return null;
        }
    }
    // 判断某一动作是否永久性改变了地图（推动木块，吃蘑菇，获取钥匙）
    private boolean map_changed(StateObservation ob){
        // 木块变动,除了推进坑的情况
        boolean brick_changed=false;
        for (int i=0; i<=1000; i++){
            try{
                Vector2d origion_brick = current_sto.ob.getMovablePositions()[1].get(i).position;
                Vector2d new_brick = ob.getMovablePositions()[1].get(i).position;
                if (!origion_brick.equals(new_brick)) brick_changed=true;
            }
            catch(Exception e){ break; }
        }
//        if (brick_changed) System.out.println("木块动了！！");
        // 分数变动（木块推进坑、吃蘑菇）
        boolean score_changed=(ob.getGameScore()!=current_sto.ob.getGameScore());
        // 钥匙变动
        boolean key_changed = false;
        try{
            Vector2d kp = new Vector2d(current_sto.ob.getMovablePositions()[0].get(0).position);
            try{
                Vector2d kkp = new Vector2d(ob.getMovablePositions()[0].get(0).position);
            }catch (Exception e){ key_changed=true; k_c = true;}
        }catch(Exception e2){}

        return (brick_changed || score_changed || key_changed);
    }
}