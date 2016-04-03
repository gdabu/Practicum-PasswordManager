package com.bcit.geoffdabu.androidechoclient;

import android.content.Context;
import android.view.View;
import android.widget.ArrayAdapter;

/**
 * Created by geoffdabu on 2016-04-03.
 */
public class Password {

    public String password;
    public String account;
    
    public Password(){
        super();
    }

    public Password(String password, String account) {
        super();
        this.password = password;
        this.account = account;
    }

    public String getPassword(){
        return password;
    }

    public String getAccount(){
        return account;
    }

    @Override
    public String toString() {
        return this.account;
    }
}
