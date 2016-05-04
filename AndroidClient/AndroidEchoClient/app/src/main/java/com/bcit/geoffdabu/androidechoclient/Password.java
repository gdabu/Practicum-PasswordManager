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

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    private String username;
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
    public Password(String account, String password,  String username) {
        super();
        this.password = password;
        this.account = account;
        this.username = username;
    }

    public String getPassword(){
        return this.password;
    }
    public int getId(){
        return id;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setAccount(String account) {
        this.account = account;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getAccount(){
        return this.account;
    }

    @Override
    public String toString() {
        return this.account;
    }
}
