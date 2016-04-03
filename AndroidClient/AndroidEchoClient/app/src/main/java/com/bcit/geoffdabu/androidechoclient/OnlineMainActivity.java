package com.bcit.geoffdabu.androidechoclient;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.IBinder;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class OnlineMainActivity extends AppCompatActivity {
    private static SocketService mBoundService;
    boolean mIsBound = false;

    private NetworkTask mNetworkTask = null;
    private ListView mainListView;
    private ArrayAdapter<Password> listAdapter;
//    private PasswordAdapter passwordAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_online_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);

        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("Password List");


        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();

                JSONObject commandData = new JSONObject();


                try {
                    commandData.put("action", "CRUD");
                    commandData.put("subaction", "READ");

                    mNetworkTask = new NetworkTask(commandData);
                    mNetworkTask.execute((Void) null);


                } catch (JSONException e) {

                    e.printStackTrace();

                }
            }
        });

        doBindService();
    }

    private void doBindService() {
        bindService(new Intent(OnlineMainActivity.this, SocketService.class), mConnection, Context.BIND_AUTO_CREATE);
        mIsBound = true;

        if (mBoundService != null) {
            mBoundService.IsBoundable();
        }
    }


    private void doUnbindService() {
        if (mIsBound) {
            // Detach our existing connection.
            unbindService(mConnection);
            mIsBound = false;
        }
    }

    protected void onDestroy() {
        super.onDestroy();
        doUnbindService();
    }


    /*
    *
    * ServiceConnection
    *
    * Network Task
    *
    *
    *
    *
    *
    *
    *
    *
    * */

    private ServiceConnection mConnection = new ServiceConnection() {
        //EDITED PART
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            // TODO Auto-generated method stub
            System.out.println("connected");
            mBoundService = ((SocketService.LocalBinder) service).getService();

            JSONObject commandData = new JSONObject();


            try {
                commandData.put("action", "CRUD");
                commandData.put("subaction", "READ");

                mNetworkTask = new NetworkTask(commandData);
                mNetworkTask.execute((Void) null);


            } catch (JSONException e) {

                e.printStackTrace();

            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            // TODO Auto-generated method stub
            mBoundService = null;
        }

    };




    /*
    *
    * AsyncTask
    *
    * Network Task
    *
    *
    *
    *
    *
    *
    *
    *
    * */

    public class NetworkTask extends AsyncTask<Void, Void, Boolean> {

        private final JSONObject sendJsonObject;
        private JSONObject recvJsonObject;


        NetworkTask(JSONObject message) {
            this.sendJsonObject = message;
        }

        @Override
        protected Boolean doInBackground(Void... params) {
            if (mBoundService != null) {
                recvJsonObject = mBoundService.sendMessage(sendJsonObject.toString());
            } else {
                System.out.println("not connected");
            }

            if (recvJsonObject == null) {
                return false;
            }


            System.out.println(recvJsonObject);
            return true;
        }

        @Override
        protected void onPostExecute(final Boolean success) {

            System.out.println("IN POST EXECUTE");
            try {

                if (recvJsonObject.getString("action").equals("CRUD")) {
                    final JSONArray passwordList = recvJsonObject.getJSONObject("additional").getJSONArray("passwords");


                    // Find the ListView resource.
                    mainListView = (ListView) findViewById(R.id.mainListView);
                    final Password[] passwords = new Password[passwordList.length()];

                    for (int i = 0; i < passwordList.length(); i++) {
                        passwords[i] = new Password(passwordList.getJSONObject(i).getString("account"), passwordList.getJSONObject(i).getString("password"));
                    }

                    // Create ArrayAdapter using the planet list.
                    listAdapter = new ArrayAdapter<Password>(OnlineMainActivity.this, R.layout.listitem, passwords);



                    mainListView.setOnItemClickListener((new AdapterView.OnItemClickListener() {

                        public void onItemClick(AdapterView<?> arg0, View view,
                                                       int index, long arg3) {
                            final Snackbar snackBar = Snackbar.make(view, "Password: " +  passwords[index].getPassword(), Snackbar.LENGTH_INDEFINITE);


                            snackBar.setAction("Hide", new View.OnClickListener() {
                                @Override
                                public void onClick(View v) {
                                    return;
                                }
                            });
                            snackBar.show();
                            return;
                        }
                    }));

                    mainListView.setOnItemLongClickListener((new AdapterView.OnItemLongClickListener() {

                        public boolean onItemLongClick(AdapterView<?> arg0, View view,
                                                       int index, long arg3) {
                            final Snackbar snackBar = Snackbar.make(view, "Would you like to delete this entry?", Snackbar.LENGTH_LONG);


                            snackBar.setAction("Confirm", new View.OnClickListener() {
                                @Override
                                public void onClick(View v) {

                                    JSONObject commandData = new JSONObject();

                                    // TODO: SEND DELETE COMMAND TO SERVER
//                                    try {
//                                        commandData.put("action", "CRUD");
//                                        commandData.put("subaction", "READ");
//
//                                        mNetworkTask = new NetworkTask(commandData);
//                                        mNetworkTask.execute((Void) null);
//
//
//                                    } catch (JSONException e) {
//
//                                        e.printStackTrace();
//
//                                    }

                                    return;
                                }
                            });
                            snackBar.show();
                            return true;
                        }
                    }));





                    // Set the ArrayAdapter as the ListView's adapter.
                    mainListView.setAdapter(listAdapter);

                }


            } catch (Exception e) {
                e.printStackTrace();
            }

            return;
        }

        @Override
        protected void onCancelled() {
            mNetworkTask = null;
        }
    }

}
