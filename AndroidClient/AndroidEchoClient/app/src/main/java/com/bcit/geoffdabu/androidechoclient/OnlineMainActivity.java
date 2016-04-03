package com.bcit.geoffdabu.androidechoclient;

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.DialogFragment;
import android.content.ComponentName;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.IBinder;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.InputType;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class OnlineMainActivity extends AppCompatActivity {
    private static SocketService mBoundService;
    boolean mIsBound = false;

    private NetworkTask mNetworkTask = null;
    private ListView mainListView;
    private ArrayAdapter<Password> listAdapter;

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


                AlertDialog.Builder builder = new AlertDialog.Builder(OnlineMainActivity.this);
                builder.setTitle("Add New Password");


                // Set up the input
                final EditText input = new EditText(OnlineMainActivity.this);
                input.setInputType(InputType.TYPE_CLASS_TEXT);
                input.setHint("Account");

                final EditText input2 = new EditText(OnlineMainActivity.this);
                input2.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
                input2.setHint("Password");

                LinearLayout ll=new LinearLayout(OnlineMainActivity.this);
                ll.setOrientation(LinearLayout.VERTICAL);
                ll.addView(input);
                ll.addView(input2);
                ll.setPadding(60,20,60,0);
                builder.setView(ll);

                // Set up the buttons
                builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String account = input.getText().toString();
                        String password = input2.getText().toString();
                        JSONObject commandData = new JSONObject();
                        try {
                            commandData.put("action", "CRUD");
                            commandData.put("subaction", "CREATE");
                            commandData.put("entry", new JSONObject().put("account", account).put("accountPassword", password));

                            mNetworkTask = new NetworkTask(commandData);
                            mNetworkTask.execute((Void) null);

                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                });
                builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                    }
                });

                builder.show();


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

        private void crudReadResponseHandler() throws JSONException {
            final JSONArray passwordList = recvJsonObject.getJSONObject("additional").getJSONArray("passwords");

            // Find the ListView resource.
            mainListView = (ListView) findViewById(R.id.mainListView);
            final Password[] passwords = new Password[passwordList.length()];

            for (int i = 0; i < passwordList.length(); i++) {
                passwords[i] = new Password(passwordList.getJSONObject(i).getString("account"), passwordList.getJSONObject(i).getString("password"), passwordList.getJSONObject(i).getInt("id"));
            }

            // Create ArrayAdapter using the planet list.
            listAdapter = new ArrayAdapter<Password>(OnlineMainActivity.this, R.layout.listitem, passwords);


            mainListView.setOnItemClickListener((new AdapterView.OnItemClickListener() {

                public void onItemClick(AdapterView<?> arg0, View view,
                                        int index, long arg3) {
                    final Snackbar snackBar = Snackbar.make(view, "Password: " + passwords[index].getPassword(), Snackbar.LENGTH_INDEFINITE);


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
                                               final int index, long arg3) {
                    new AlertDialog.Builder(OnlineMainActivity.this)
                            .setTitle("Delete Password")
                            .setMessage("Are you sure you want to delete this password?")
                            .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    // continue with delete
                                    JSONObject commandData = new JSONObject();
                                    try {
                                        commandData.put("action", "CRUD");
                                        commandData.put("subaction", "DELETE");
                                        commandData.put("entry", new JSONObject().put("id", passwords[index].getId()));

                                        mNetworkTask = new NetworkTask(commandData);
                                        mNetworkTask.execute((Void) null);

                                    } catch (JSONException e) {
                                        e.printStackTrace();
                                    }
                                }
                            })
                            .setNegativeButton(android.R.string.no, new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    // do nothing
                                }
                            })
                            .setIcon(android.R.drawable.ic_delete)
                            .show();
                    return true;
                }
            }));


            // Set the ArrayAdapter as the ListView's adapter.
            mainListView.setAdapter(listAdapter);

            return;
        }

        @Override
        protected void onPostExecute(final Boolean success) {

            System.out.println("IN POST EXECUTE");
            try {

                if (recvJsonObject.getString("action").equals("CRUD")) {

                    if (recvJsonObject.getJSONObject("additional").getString("subaction").equals("READ")) {
                        crudReadResponseHandler();
                    } else {
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

                }
            } catch (JSONException e) {
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
