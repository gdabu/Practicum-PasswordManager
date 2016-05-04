package com.bcit.geoffdabu.androidechoclient;

/**
 * Created by geoffdabu on 2016-04-26.
 */
public class User {

    private String _username;
    private String _password;

    public User(String username, String password){
        this._username = username;
        this._password = password;
    }

    public String getPassword() {
        return _password;
    }

    public String getUsername() {
        return _username;
    }

    public void setPassword(String password) {
        this._password = password;
    }

    public void setUsername(String username) {
        this._username = username;
    }
}
