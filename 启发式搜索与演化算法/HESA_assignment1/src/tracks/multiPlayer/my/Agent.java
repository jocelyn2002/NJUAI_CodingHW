package tracks.multiPlayer.my;

import core.game.Observation;
import core.game.StateObservationMulti;
import core.player.AbstractMultiPlayer;
import ontology.Types;
import tools.ElapsedCpuTimer;
import tools.Vector2d;

import java.util.*;



public class Agent extends AbstractMultiPlayer {
	int id; // this player's ID
	int oppid; // 对手的id
	ArrayList<AStarNode> frontier;
	ArrayList<AStarNode> searched;
	AStarNode root;
	double stepCost=100;
	int blocksz;
	ArrayList<Types.ACTIONS> actions;
	Random rand;
	int width,height;
	int[][] walls;

	// 创建agent
	public Agent(StateObservationMulti stateObs, ElapsedCpuTimer elapsedTimer, int playerID) {
		id = playerID;
		oppid = 1-playerID;
		blocksz = stateObs.getBlockSize();
		actions = stateObs.getAvailableActions(oppid);
		rand = new Random(2020);
		width = stateObs.getObservationGrid().length;
		height = stateObs.getObservationGrid()[0].length;
//        System.out.println(width+" "+height);
		walls = new int[width][height];
		for (Observation obi :stateObs.getImmovablePositions()[0]) {
			int x = (int)obi.position.x/blocksz;
			int y = (int)obi.position.y/blocksz;
			while (y>=height) y--;
			while (y<0) y++;
			while (x>=width) x--;
			while (x<0) x++;
			walls[x][y] = 1;
		}
	}

	// 执行一次行动
	@Override
	public Types.ACTIONS act(StateObservationMulti stateObs, ElapsedCpuTimer elapsedTimer) {
		frontier = new ArrayList<>();
		searched = new ArrayList<>();


		root = new AStarNode(stateObs,null, actions.get(4) ,0,0);
		frontier.add(root);


		// 搜索过程
		double avgTimeTaken = 0;
		double acumTimeTaken = 0;
		double worstTimeTaken = 0;
		long remaining = elapsedTimer.remainingTimeMillis();
		int numIters = 0;

		while(remaining > 2*avgTimeTaken && remaining > worstTimeTaken){
			ElapsedCpuTimer elapsedTimerIteration = new ElapsedCpuTimer();


			// 从前线选择最佳节点
			// 当遍历完全则提前结束
			if (frontier.size()==0) {
//                System.out.println(id+"  early stop");
				break;
			}
			frontier.sort(new Comparator<AStarNode>() {
				@Override
				public int compare(AStarNode n1, AStarNode n2) {
					return Double.compare(n1.f_value, n2.f_value);
				}
			});
			AStarNode pick = frontier.remove(0);


			// 扩展节点
			for (Types.ACTIONS a:actions) {
				StateObservationMulti ob = pick.state.copy();

				Types.ACTIONS[] acts = new Types.ACTIONS[2]; // 二人游戏
				acts[id] = a;
				acts[oppid] = getNoLoseAct(ob,oppid);
				ob.advance(acts);


				// 没动的情况(TODO:排除由于对方撞墙导致自己不能动，在getOppAct中实现)
				if (eqState(ob,stateObs,id)) {
//                    System.out.println("No move");
				}
				// 节点已经搜索过
				else if (DiscoveredState(ob,searched)!=null) {
//                    System.out.println("Searched");
				}
				else {
					// 节点已被加入前线
					AStarNode node = DiscoveredState(ob, frontier);
					if (node!=null) {
//                      // 新f_value比原来小，更新父节点
						if (node.f_value > pick.g_value + stepCost + h(ob)) {
							node.update_father(pick,a, pick.g_value+stepCost,h(ob));
						}
						// 新f_Value不比原来小，则什么都不用做
					}
					// 全新节点，加入前线
					else {
						AStarNode tmpNode = new AStarNode(ob, pick, a, pick.g_value + stepCost, h(ob));
						frontier.add(tmpNode);
					}
				}

			}

			searched.add(pick);

			// 时间统计
			numIters++;
			acumTimeTaken += (elapsedTimerIteration.elapsedMillis());
			avgTimeTaken  = acumTimeTaken/numIters;
			remaining = elapsedTimer.remainingTimeMillis();
			if (elapsedTimerIteration.elapsedMillis()>worstTimeTaken)
				worstTimeTaken = elapsedTimerIteration.elapsedMillis();
		}

		System.out.println(id+"  "+numIters);


		// 决策过程
		Types.ACTIONS best_act;
		if (frontier.size()>0) {
			best_act = getBestAct(frontier);
		}
		else if (searched.size()>0){
			best_act = getBestAct(searched);
		}
		else {
			best_act = actions.get(rand.nextInt(actions.size()));
			System.out.println(id+" RandomAct "+best_act.name());
		}

		return best_act;
	}

	int score_cost = -1000;
	int dif_cost = 500; // 比score cost大，使得不会为了吃金币而穿墙
	int ghost_dis_cost = 1000; // 比dif_cost大，使得追猎ghost时可以穿墙
	int power_const = -12000; // 1000*12，用于奖励进入power状态，防止h(s)反常上升
	int resource_dis_cost = 100; // 不用很大，只需要在没有方向的时候提供一个启发
	int hunt_npc = 2; // 每个Avatar追猎的ghost数量，一个追[:hunt_npc],另一个追[hunt_npc:]，防止抢夺导致死锁
	// 启发式函数
	public double h(StateObservationMulti ob) {
		// 0.确保尽量不让自己死掉
		if (ob.isGameOver()) return Double.MAX_VALUE / 2;

		// 自己的坐标
		int xAvatar = (int)ob.getAvatarPosition(id).x / blocksz;
		int yAvatar = (int)ob.getAvatarPosition(id).y / blocksz;


		double value = 0;
		// 1.游戏得分直接计入
		value += score_cost * ob.getGameScore(id);

		// 2.尽量不要改变地图（经验得出更改地图往往不利）
		int[][] newwalls = new int[width][height];
		for (Observation obi :ob.getImmovablePositions()[0]) {
			int x = (int)obi.position.x/blocksz;
			int y = (int)obi.position.y/blocksz;
			while (y>=height) y--;
			while (y<0) y++;
			while (x>=width) x--;
			while (x<0) x++;
			newwalls[x][y] = 1;
		}
		int diff = 0;
		for (int i=1;i<width-1;i++)
			for (int j=1;j<height-1;j++)
				diff += Math.abs(walls[i][j]-newwalls[i][j]);
		value += dif_cost*diff;

		// 3.在powered状态，寻找最近的ghost（经过检验 0号agent充能前后type为28->29  1号为31->32
		// TODO：应该避免重复Powered,节约绿宝石
		try { // 有一定概率出现奇怪的bug，因此用try
			if (id == 0 && ob.getAvatarType(0) == 29) {
				int mindis = 1000;
				for (int nnpc = 0; nnpc < hunt_npc; nnpc++) {
					mindis = getNPCdis(ob, xAvatar, yAvatar, mindis, nnpc);
				}
				value += ghost_dis_cost * mindis;
				value += power_const;
			}
			else if (id == 1 && ob.getAvatarType(1) == 32) {
				int mindis = 1000;
				for (int nnpc = ob.getNPCPositions().length-1; nnpc >= ob.getNPCPositions().length-hunt_npc; nnpc--) {
					mindis = getNPCdis(ob, xAvatar, yAvatar, mindis, nnpc);
				}
				value += ghost_dis_cost * mindis;
				value += power_const;
			}
		}catch(Exception e){
//            System.out.println("fuck!!  "+ob.getNPCPositions().length);
		}
		// 4.在非Powered状态，优先寻找绿宝石4、樱桃2、金币3
		if ((id == 0 && ob.getAvatarType(0) == 28) || (id == 1 && ob.getAvatarType(1) == 31)) {
			int mindis = 1000;
			int index = ob.getImmovablePositions().length-1;
			for (int nresource = 0; nresource < ob.getImmovablePositions()[index].size(); nresource++) {
				int xresource = (int) ob.getImmovablePositions()[index].get(nresource).position.x / blocksz;
				int yresource = (int) ob.getImmovablePositions()[index].get(nresource).position.y / blocksz;
				int distance = Math.abs(xAvatar - xresource) + Math.abs(yAvatar - yresource);
				if (distance < mindis)
					mindis = distance;
			}
			value += resource_dis_cost * mindis;
		}


		return rand.nextInt(10) + value;
	}

	// 获取nnpc对应编号的ghost与id对应编号Avatar的距离
	private int getNPCdis(StateObservationMulti ob, int xAvatar, int yAvatar, int mindis, int nnpc) {
		int xnpc = (int) ob.getNPCPositions()[nnpc].get(0).position.x / blocksz;
		int ynpc = (int) ob.getNPCPositions()[nnpc].get(0).position.y / blocksz;
		int distance = Math.min(Math.abs(xAvatar - xnpc),width-Math.abs(xAvatar-xnpc)) + Math.min(Math.abs(yAvatar - ynpc),height-Math.abs(yAvatar-ynpc));
		if (distance < mindis)
			mindis = distance;
		return mindis;
	}

	// 从某一列表中获得最佳行动
	private Types.ACTIONS getBestAct(ArrayList<AStarNode> list) {
		Types.ACTIONS best_act;
		list.sort(new Comparator<AStarNode>() {
			@Override
			public int compare(AStarNode n1, AStarNode n2) {
				return Double.compare(n1.f_value, n2.f_value);
			}
		});
		AStarNode tmpNode = list.get(0);
		best_act = tmpNode.act;
		while (tmpNode.father != null) {
			best_act = tmpNode.act;
			tmpNode = tmpNode.father;
		}
		System.out.println(id+" BestAct "+best_act.name());
		return best_act;
	}

	// 获取对手状态，用于模拟前进
	public Types.ACTIONS getNoLoseAct(StateObservationMulti ob,int player) {
		for (int i=4;i>=0;i--)
			for (int j=4;j>=0;j--){
				StateObservationMulti obcp = ob.copy();
				Types.ACTIONS[] acts = new Types.ACTIONS[2]; // 二人游戏
				acts[player] = actions.get(i);
				acts[1-player] = actions.get(j);
				obcp.advance(acts);
				if (!obcp.isGameOver()) return actions.get(i);
			}
		return actions.get(4);
	}

	// 判断两个状态是否相同，若player为-1则判断完整状态，若传递player则只看他的位置是否变化
	public boolean eqState(StateObservationMulti ob1, StateObservationMulti ob2, int player) {
		// 判断全局是否变化
		if (player==-1) {
			if (ob1.getImmovablePositions().length!=ob2.getImmovablePositions().length) return false;
			else
				for (int j=0;j<ob1.getImmovablePositions().length;j++) {
					if (ob1.getImmovablePositions()[j].size() != ob2.getImmovablePositions()[j].size()) {
						return false;
					}
				}
			Vector2d pos1 = ob1.getAvatarPosition(0);
			Vector2d pos2 = ob2.getAvatarPosition(0);
			Vector2d pos3 = ob1.getAvatarPosition(1);
			Vector2d pos4 = ob2.getAvatarPosition(1);
			return pos1.equals(pos2)&&pos3.equals(pos4);
		}
		// 判断某个Avatar位置单步是否改变
		else {
			Vector2d pos1 = ob1.getAvatarPosition(player);
			Vector2d pos2 = ob2.getAvatarPosition(player);
			return pos1.equals(pos2);
		}
	}

	// 判断某个状态是否已经在某个list中
	public AStarNode DiscoveredState(StateObservationMulti ob, ArrayList<AStarNode> l) {
		for (AStarNode node :l) {
			if (eqState(node.state,ob,-1)) {
				return node;
			}
		}
		return null;
	}

	// 打印状态的某些信息
	public void printState(StateObservationMulti ob) {
//        System.out.println(stateObs.getAvatarType(0)+" "+stateObs.getAvatarType(1));

//        System.out.println(id+": "+stateObs.getPortalsPositions()[0]); // 奇怪的位置（推测为不存在的“门”）
//        System.out.println(id+": "+stateObs.getMovablePositions()); // 始终为null
//        System.out.println(id+": "+stateObs.getResourcesPositions()); // 始终为null
//        System.out.println(id+": "+stateObs.getFromAvatarSpritesPositions()); // 始终为null
//        System.out.println(id+": "+stateObs.getGameState()); // 始终为null


//        System.out.println(id+": "+stateObs.getImmovablePositions()[0]); // 墙体
//        System.out.println(id+": "+stateObs.getImmovablePositions()[1]); // 地板
//        System.out.println(id+": "+stateObs.getImmovablePositions()[2]); // fruit
//        System.out.println(id+": "+stateObs.getImmovablePositions()[3]); // pellet
//        System.out.println(id+": "+stateObs.getImmovablePositions()[4]); // power

//        System.out.println(id+": "+stateObs.getNPCPositions().length); // 初次访问为空，之后为4个ghost的位置
//        System.out.println(stateObs.getAvatarPosition(id)); // 对应id Avatar位置，缺省为0号Avatar


//        stateObs.getObservationGrid();
		System.out.print("("+(int)ob.getAvatarPosition(id).x/blocksz+","+(int)ob.getAvatarPosition(id).y/blocksz+") ");
	}
}