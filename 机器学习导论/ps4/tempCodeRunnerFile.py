    y_out = [1 if y_pred[i]>0.5 else 0 for i in range(len(y_pred))]
    np.savetxt("./181220010_ypred.csv",y_out,delimiter=",")