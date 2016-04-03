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

    public Password(String password, String account, int id) {
        super();
        this.password = password;
        this.account = account;
        this.id = id;
    }

    public String getPassword(){
        return password;
    }
    public int getId(){
        return id;
    }


    public String getAccount(){
        return account;
    }

    @Override
    public String toString() {
        return this.account;
    }
}
