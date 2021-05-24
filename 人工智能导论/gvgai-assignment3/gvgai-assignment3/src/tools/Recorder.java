/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tools;

import core.game.Observation;
import core.game.StateObservation;

import java.io.FileWriter;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Observable;

import ontology.Types;
import weka.core.Attribute;
import weka.core.FastVector;
import weka.core.Instances;

/**
 *
 * @author yuy
 */
public class Recorder {
    public FileWriter filewriter;
    public static Instances s_datasetHeader = datasetHeader();
    private static int last_act;

    public Recorder(String filename) throws Exception {

        filewriter = new FileWriter(filename + ".arff");
        filewriter.write(s_datasetHeader.toString());
        /*
                // ARFF File header
        filewriter.write("@RELATION AliensData\n");
        // Each row denotes the feature attribute
        // In this demo, the features have four dimensions.
        filewriter.write("@ATTRIBUTE gameScore  NUMERIC\n");
        filewriter.write("@ATTRIBUTE avatarSpeed  NUMERIC\n");
        filewriter.write("@ATTRIBUTE avatarHealthPoints NUMERIC\n");
        filewriter.write("@ATTRIBUTE avatarType NUMERIC\n");
        // objects
        for(int y=0; y<14; y++)
            for(int x=0; x<32; x++)
                filewriter.write("@ATTRIBUTE object_at_position_x=" + x + "_y=" + y + " NUMERIC\n");
        // The last row of the ARFF header stands for the classes
        filewriter.write("@ATTRIBUTE Class {0,1,2}\n");
        // The data will recorded in the following.
        filewriter.write("@Data\n");*/

    }

    public static double[] featureExtract(StateObservation obs) {

        double[] feature = new double[453];  // 448 + 4 + 1(class)

        // 448 locations
        int[][] map = new int[32][14];
        // Extract features
        LinkedList<Observation> allobj = new LinkedList<>();
        if (obs.getImmovablePositions() != null)
            for (ArrayList<Observation> l : obs.getImmovablePositions()) allobj.addAll(l);
        if (obs.getMovablePositions() != null)
            for (ArrayList<Observation> l : obs.getMovablePositions()) allobj.addAll(l);
        if (obs.getNPCPositions() != null)
            for (ArrayList<Observation> l : obs.getNPCPositions()) allobj.addAll(l);

        Vector2d ap = obs.getAvatarPosition();
        double ax = ap.x/25;

        for (Observation o : allobj) {
            Vector2d p = o.position;
            int x = (int) (p.x / 25);
            int y = (int) (p.y / 25);
            map[x][y] = o.itype;

        }

//        System.out.println(ax);

        boolean not_found = true;
        for (int y = 13; y >=0; y--)
            for (int x = 31; x >= 0; x--) {
                feature[y * 32 + x] = map[x][y];
                if (not_found && map[x][y]==6) {feature[449]=x-ax;not_found=false;}
            }

        // 4 states
        feature[448] = obs.getGameTick();
//        feature[449] = obs.getAvatarSpeed();
//        feature[450] = obs.getAvatarHealthPoints();
//        feature[451] = obs.getAvatarType();

        boolean found=false;
        for (int eps=0;eps<=5;eps++){
            if (ax-eps>=0)
                for (int yy=0;yy<14;yy++)
                    if (map[(int)ax-eps][yy]==5){
                        feature[450]=-eps;
                        found=true;
                        break;
                    }
            if (ax+eps<14)
                for (int yy=0;yy<14;yy++)
                    if (map[(int)ax+eps][yy]==5){
                        feature[450]=eps;
                        found=true;
                        break;
                    }
            if (found) break;
        }

        feature[451] = last_act;

        return feature;
    }

    public static Instances datasetHeader() {
        FastVector attInfo = new FastVector();
        // 448 locations
        for (int y = 0; y < 14; y++) {
            for (int x = 0; x < 32; x++) {
                Attribute att = new Attribute("object_at_position_x=" + x + "_y=" + y);
                attInfo.addElement(att);
            }
        }
        Attribute att = new Attribute("GameTick");
        attInfo.addElement(att);
//        att = new Attribute("AvatarSpeed");
        att = new Attribute("FirstAlienPosition");
        attInfo.addElement(att);
//        att = new Attribute("AvatarHealthPoints");
        att = new Attribute("NearestBombPosition");
        attInfo.addElement(att);
//        att = new Attribute("AvatarType");
        att = new Attribute("LastAct");
        attInfo.addElement(att);
        //class
        FastVector classes = new FastVector();
        classes.addElement("0");
        classes.addElement("1");
        classes.addElement("2");
        classes.addElement("3");
        att = new Attribute("class", classes);
        attInfo.addElement(att);



        Instances instances = new Instances("AliensData", attInfo, 0);
        instances.setClassIndex(instances.numAttributes() - 1);

        return instances;
    }

    // Record each move as the ARFF instance
    public void invoke(StateObservation obs, Types.ACTIONS action) {
        double[] feature = featureExtract(obs);

        try {
            for (int i = 0; i < feature.length - 1; i++)
                filewriter.write(feature[i] + ",");
            // Recorde the move type as ARFF classes
            int action_num = 0;
            if (Types.ACTIONS.ACTION_NIL == action) last_act=action_num = 0;
            if (Types.ACTIONS.ACTION_USE == action) last_act=action_num = 1;
            if (Types.ACTIONS.ACTION_LEFT == action) last_act=action_num = 2;
            if (Types.ACTIONS.ACTION_RIGHT == action) last_act=action_num = 3;
            filewriter.write(action_num + "\n");
            filewriter.flush();
        } catch (Exception exc) {
            exc.printStackTrace();
        }
    }

    public void close() {
        try {
            filewriter.close();
        } catch (Exception exc) {
            exc.printStackTrace();
        }
    }
}