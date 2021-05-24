package controllers.Astar;

import core.game.StateObservation;
import ontology.Types;

public class STO{
    // 父亲节点
    public STO myfather;
    // 父亲节点通过什么动作来到这里
    public Types.ACTIONS fatheraction;
    // 自己
    public StateObservation ob;
    // 自己的价值
    public double cost;
    // 自己的深度（根为0）
    public int depth;
    // 构造函数

    public STO(StateObservation me, STO father, Types.ACTIONS act,int deep,double cos){
        myfather=father;
        ob=me;
        fatheraction=act;
        cost = cos;
        depth = deep;
    }
}