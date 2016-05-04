package com.bcit.geoffdabu.androidechoclient;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/**
 * Created by geoffdabu on 2016-04-26.
 */
public class PasswordDatabaseHandler extends SQLiteOpenHelper {
    // All Static variables
    // Database Version
    private static final int DATABASE_VERSION = 2;

    // Database Name
    private static final String DATABASE_NAME = "pwd_manager";

    // Contacts table name
    private static final String TABLE_USERS = "users";

    // Contacts Table Columns names
    private static final String KEY_USERNAME = "username";
    private static final String KEY_PASSWORD = "password";

    public PasswordDatabaseHandler(Context context) {
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
    }

    // Upgrading database
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // Drop older table if existed
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_USERS);

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

}
