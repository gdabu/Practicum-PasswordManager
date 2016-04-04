package com.bcit.geoffdabu.androidechoclient;

import android.content.Context;
import android.view.View;
import android.widget.ArrayAdapter;

/**
 * Created by geoffdabu on 2016-04-03.
 */
public class Password {

    private String password;
    private String account;
    private int id;
    
    public Password(){
        super();
    }

    public Password(String account, String password,  int id) {
        super();
        this.password = password;
        this.account = account;
        this.id = id;
    }

    public String getPassword(){
        return this.password;
    }
    public int getId(){
        return id;
    }



    public String getAccount(){
        return this.account;
    }

    @Override
    public String toString() {
        return this.account;
    }
}
