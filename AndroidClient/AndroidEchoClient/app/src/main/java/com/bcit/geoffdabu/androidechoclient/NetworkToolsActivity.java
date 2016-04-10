package com.bcit.geoffdabu.androidechoclient;

import android.app.AlertDialog;
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
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class NetworkToolsActivity extends AppCompatActivity {

    private static SocketService mBoundService;
    boolean mIsBound = false;

    private NetworkTask mNetworkTask = null;
    private ListView mainListView;
    private ArrayAdapter<Password> listAdapter;

    private DrawerLayout mDrawerLayout;
    private ListView mDrawerList;


    private ProgressBar bar;

    private class DrawerItemClickListener implements ListView.OnItemClickListener {
        @Override
        public void onItemClick(AdapterView parent, View view, int position, long id) {
            System.out.println(parent);
            selectItem(position);

        }
    }

    /** Swaps fragments in the main content view */
    private void selectItem(int position) {
        // Create a new fragment and specify the planet to show based on position
        if(position == 0){
            finish();
            Intent i = new Intent(getApplicationContext(), OnlineMainActivity.class);
            startActivity(i);
        }else if (position == 2){
            finish();
            Intent i = new Intent(getApplicationContext(), LoginActivity.class);
            startActivity(i);
        }
    }

    private ActionBarDrawerToggle mDrawerToggle;


    public boolean onOptionsItemSelected(MenuItem item) {
        // Pass the event to ActionBarDrawerToggle, if it returns
        // true, then it has handled the app icon touch event
        if (mDrawerToggle.onOptionsItemSelected(item)) {
            return true;
        }
        // Handle your other action bar items...

        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_network_tools);



        String[] mPlanetTitles = { "Password List", "Network Scan", "Logout"};
        mDrawerLayout = (DrawerLayout) findViewById(R.id.drawer_layout);
        mDrawerList = (ListView) findViewById(R.id.left_drawer);

        // Set the adapter for the list view
        mDrawerList.setAdapter(new ArrayAdapter<String>(this,
                R.layout.listitem, mPlanetTitles));
        // Set the list's click listener
        mDrawerList.setOnItemClickListener(new DrawerItemClickListener());

        Toast.makeText(this, "Scanning Server Network...", Toast.LENGTH_LONG).show();

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Toast.makeText(NetworkToolsActivity.this, "Scanning Server Network...", Toast.LENGTH_LONG).show();
                JSONObject commandData = new JSONObject();


                try {
                    commandData.put("action", "SCAN");

                    mNetworkTask = new NetworkTask(commandData);
                    mNetworkTask.execute((Void) null);


                } catch (JSONException e) {

                    e.printStackTrace();

                }
            }
        });

        getSupportActionBar().setHomeButtonEnabled(true);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);

        mDrawerToggle = new ActionBarDrawerToggle(this, mDrawerLayout, 0, 0){

            @Override
            public void onDrawerClosed(View view) {
                super.onDrawerClosed(view);
                invalidateOptionsMenu(); // creates call to onPrepareOptionsMenu()
                syncState();
            }

            @Override
            public void onDrawerOpened(View drawerView) {
                super.onDrawerOpened(drawerView);
                invalidateOptionsMenu(); // creates call to onPrepareOptionsMenu()
                syncState();
            }
        };


        mDrawerLayout.setDrawerListener(mDrawerToggle);


        mDrawerToggle.syncState();


        bar = (ProgressBar) this.findViewById(R.id.progressBar);


        doBindService();
    }

    private void doBindService() {
        bindService(new Intent(NetworkToolsActivity.this, SocketService.class), mConnection, Context.BIND_AUTO_CREATE);
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
                commandData.put("action", "SCAN");

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
        protected void onPreExecute(){
            bar.setVisibility(View.VISIBLE);
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
            listAdapter = new ArrayAdapter<Password>(NetworkToolsActivity.this, R.layout.listitem, passwords);


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
                    new AlertDialog.Builder(NetworkToolsActivity.this)
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
                            .setIcon(R.drawable.ic_warning_black_48dp)
                            .show();
                    return true;
                }
            }));


            // Set the ArrayAdapter as the ListView's adapter.
            mainListView.setAdapter(listAdapter);

            return;
        }
        private ArrayAdapter<String> hostListAdapter ;

        private void scanResponseHandler() throws JSONException{
            final JSONArray hostList = recvJsonObject.getJSONObject("additional").getJSONArray("hosts");
            mainListView = (ListView) findViewById(R.id.hostListView);
            ArrayList<String> hosts = new ArrayList<String>();

            hostListAdapter = new ArrayAdapter<String>(NetworkToolsActivity.this, R.layout.listitem, hosts);

            for (int i = 0; i < hostList.length(); i++) {
                hostListAdapter.add(hostList.getJSONObject(i).getString("host"));
            }

            mainListView.setAdapter(hostListAdapter);

        }

        @Override
        protected void onPostExecute(final Boolean success) {

            bar.setVisibility(View.GONE);
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
                }else if(recvJsonObject.getString("action").equals("SCAN")){
                    scanResponseHandler();
                    Toast.makeText(NetworkToolsActivity.this, "Scan Complete!", Toast.LENGTH_LONG).show();

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
