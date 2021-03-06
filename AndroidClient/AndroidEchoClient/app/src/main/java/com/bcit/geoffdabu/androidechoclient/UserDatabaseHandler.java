package com.bcit.geoffdabu.androidechoclient;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by geoffdabu on 2016-04-26.
 */
public class UserDatabaseHandler extends SQLiteOpenHelper {
    // All Static variables
    // Database Version
    private static final int DATABASE_VERSION = 8;

    // Database Name
    private static final String DATABASE_NAME = "pwd_manager";

    // Contacts table name
    private static final String TABLE_USERS = "users";
    private static final String TABLE_PASSWORDS = "passwords";

    // Contacts Table Columns names
    private static final String KEY_USERNAME = "username";
    private static final String KEY_PASSWORD = "password";

    private static final String KEY_ID = "id";
    private static final String KEY_ACCOUNT = "account";

    public UserDatabaseHandler(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    // Creating Tables
    @Override
    public void onCreate(SQLiteDatabase db) {
        String CREATE_CONTACTS_TABLE = "CREATE TABLE " + TABLE_USERS + "("
                + KEY_USERNAME + " TEXT,"
                + KEY_PASSWORD + " TEXT, "
                + "PRIMARY KEY('" + KEY_USERNAME + "'))";
        db.execSQL(CREATE_CONTACTS_TABLE);

        String CREATE_PASSWORDS_TABLE = "CREATE TABLE " + TABLE_PASSWORDS + "("
                + KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + KEY_USERNAME + " TEXT,"
                + KEY_ACCOUNT + " TEXT,"
                + KEY_PASSWORD + " TEXT,"
                + "FOREIGN KEY(" + KEY_USERNAME + ") REFERENCES " + TABLE_USERS + "(" + KEY_USERNAME + ")"
                +")";

        db.execSQL(CREATE_PASSWORDS_TABLE);

    }

    // Upgrading database
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // Drop older table if existed
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_USERS);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_PASSWORDS);

        // Create tables again
        onCreate(db);
    }

    // Getting single contact
    public User getUser(String username) {
        SQLiteDatabase db = this.getReadableDatabase();

        Cursor cursor = db.query(TABLE_USERS, new String[] {KEY_USERNAME, KEY_PASSWORD}, KEY_USERNAME + "=?", new String[] { String.valueOf(username) }, null, null, null, null);
        User user = null;

        if (cursor != null) {
            cursor.moveToFirst();
            user = new User(cursor.getString(0), cursor.getString(1));
        }else{
            return user;
        }
        // return contact
        return user;
    }

//
//    // Getting All Contacts
//    public List<User> getAllUsers() {}
//
//    // Getting contacts Count
//    public int getUserCount() {}
//
//    // Updating single contact
//    public int updateUser(User user) {}

    // Deleting single contact
    public void deleteUser(User user) {}

    public void addUser(User user) {
        SQLiteDatabase db = this.getWritableDatabase();

        ContentValues values = new ContentValues();
        values.put(KEY_USERNAME, user.getUsername()); // Contact Name
        values.put(KEY_PASSWORD, user.getPassword()); // Contact Phone Number

        // Inserting Row
        db.insert(TABLE_USERS, null, values);
        db.close(); // Closing database connection
    }

    public void addPassword(Password password) {
        SQLiteDatabase db = this.getWritableDatabase();

        ContentValues values = new ContentValues();
        values.put(KEY_USERNAME, password.getUsername()); // Contact Name
        values.put(KEY_PASSWORD, password.getPassword()); // Contact Phone Number
        values.put(KEY_ACCOUNT, password.getAccount());

        // Inserting Row
        db.insert(TABLE_PASSWORDS, null, values);
        db.close(); // Closing database connection
    }

    public void deletePassword(int id){
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_PASSWORDS, KEY_ID + " = ?",
                new String[]{String.valueOf(id)});
        db.close();
    }

    public void deletePasswords(String username){
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_PASSWORDS, KEY_USERNAME + " = ?",
                new String[] { String.valueOf(username) });
        db.close();
    }



    // Getting single contact
    public List<Password> getUserPasswords(String username) {

        List<Password> passwordList = new ArrayList<Password>();
        // Select All Query

        SQLiteDatabase db = this.getWritableDatabase();
        Cursor cursor = db.query(TABLE_PASSWORDS, new String[]{KEY_USERNAME, KEY_ACCOUNT, KEY_PASSWORD, KEY_ID}, KEY_USERNAME + "=?", new String[]{String.valueOf(username)}, null, null, null, null);

        // looping through all rows and adding to list
        if (cursor.moveToFirst()) {
            do {
                Password password = new Password();
                password.setUsername(cursor.getString(0));
                password.setAccount(cursor.getString(1));
                password.setPassword(cursor.getString(2));
                password.setId(Integer.parseInt(cursor.getString(3)));
                // Adding contact to list
                passwordList.add(password);
            } while (cursor.moveToNext());
        }

        // return contact list
        return passwordList;

    }

}
