/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package controllers.learningmodel;

import tools.*;
import core.game.Observation;
import core.game.StateObservation;

import java.io.FileWriter;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Observable;

import ontology.Types;
import weka.core.Attribute;
import weka.core.FastVector;
import weka.core.Instance;
import weka.core.Instances;

/**
 *
 * @author yuy
 */
public class RLDataExtractor {
    public FileWriter filewriter;
    public static Instances s_datasetHeader = datasetHeader();
    
    public RLDataExtractor(String filename) throws Exception{
        
        filewriter = new FileWriter(filename+".arff");
        filewriter.write(s_datasetHeader.toString());
    }


    private static int total =5+(2*2+1)*(2*2+1); // 2 + 25 + 1(goal_x) + 1(action) + 1(Q)


    public static Instance makeInstance(double[] features, int action, double reward){
        features[total-2] = action;
        features[total-1] = reward;
        Instance ins = new Instance(1, features);
        ins.setDataset(s_datasetHeader);
        return ins;
    }
    
    public static double[] featureExtract(StateObservation obs){
        double[] feature = new double[total];

        // 448 locations
        int[][] map = new int[28][31];
        // Extract features
        LinkedList<Observation> allobj = new LinkedList<>();
        if( obs.getImmovablePositions()!=null )
            for(ArrayList<Observation> l : obs.getImmovablePositions()) allobj.addAll(l);
        if( obs.getMovablePositions()!=null )
            for(ArrayList<Observation> l : obs.getMovablePositions()) allobj.addAll(l);
        if( obs.getNPCPositions()!=null )
            for(ArrayList<Observation> l : obs.getNPCPositions()) allobj.addAll(l);
        if (obs.getResourcesPositions()!=null)
            for(ArrayList<Observation> l : obs.getResourcesPositions()) allobj.addAll(l);
        if (obs.getPortalsPositions()!=null)
            for(ArrayList<Observation> l : obs.getPortalsPositions()) allobj.addAll(l);
        
        for(Observation o : allobj){
            Vector2d p = o.position;
            int x = (int)(p.x/28); //squre size is 28 for pacman
            int y= (int)(p.y/28);
            map[x][y] = o.itype;
        }
        // Avatar_x_y
        int xx = (int)obs.getAvatarPosition().x/28;
        feature[0] = xx;
        int yy = (int)obs.getAvatarPosition().y/28;
        feature[1] = yy;
        // 九宫格
        int co = 2;
        int true_x,true_y;
        for (int y = -2;y<=2;y++) {
            for (int x = -2; x <= 2; x++) {
                true_x = xx+x;
                true_x = true_x>0 ? true_x : true_x + 26;
                true_x = true_x<27 ? true_x : true_x - 26;
                true_y = yy+y;
                true_y = true_y>0 ? true_y : true_y + 13;
                true_y = true_y<14 ? true_y : true_y - 13;
                feature[co] = map[true_x][true_y];
                co++;
            }
        }
        // 门的x坐标
        for (int tt=0;tt<28;tt++) {
            if (map[tt][1]==4){
                feature[total-3] = tt;
                break;
            }
        }
        return feature;
    }
    
    public static Instances datasetHeader(){
        
        if (s_datasetHeader!=null)
            return s_datasetHeader;
        
        FastVector attInfo = new FastVector();
        // Avatar的x和y坐标
        Attribute att = new Attribute("Avatar_x");attInfo.addElement(att);
        att = new Attribute("Avatar_y");attInfo.addElement(att);
        // 以Avatar为核心的九宫格
        for (int y=-2;y<=2;y++){
            for (int x=-2;x<=2;x++){
                att = new Attribute("object_at_relative_position_x"+x+"_y"+y);
                attInfo.addElement(att);
            }
        }
        att = new Attribute("door_x");attInfo.addElement(att);
        //action
        FastVector actions = new FastVector();
        actions.addElement("0");
        actions.addElement("1");
        actions.addElement("2");
        actions.addElement("3");
        att = new Attribute("actions", actions);        
        attInfo.addElement(att);
        // Q value
        att = new Attribute("Qvalue");
        attInfo.addElement(att);
        Instances instances = new Instances("PacmanQdata", attInfo, 0);
        instances.setClassIndex( instances.numAttributes() - 1);
        return instances;
    }
}
