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
import android.text.InputType;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

public class OnlineMainActivity extends AppCompatActivity {
    private static SocketService mBoundService;
    boolean mIsBound = false;

    private NetworkTask mNetworkTask = null;
    private ListView mainListView;
    private ArrayAdapter<Password> listAdapter;



    private DrawerLayout mDrawerLayout;
    private ListView mDrawerList;


    private ProgressBar bar;


    Crypt aesCrypt = new Crypt();

    UserDatabaseHandler db = new UserDatabaseHandler(OnlineMainActivity.this);


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

        }else if(position == 1){
            finish();
            Intent myIntent = getIntent(); // gets the previously created intent
            Intent i = new Intent(getApplicationContext(), NetworkToolsActivity.class);
            String username = myIntent.getStringExtra("username");
            i.putExtra("username",username);
            startActivity(i);
        }else if (position == 4){
            finish();
            Intent i = new Intent(getApplicationContext(), LoginActivity.class);
            startActivity(i);
        }else if (position == 2){

            try {
                JSONObject commandData = new JSONObject();
                commandData.put("action", "SYNC");
                commandData.put("subaction", "PULL");

                mNetworkTask = new NetworkTask(commandData);
                mNetworkTask.execute((Void) null);


            } catch (JSONException e) {

                e.printStackTrace();

            }




        }else if(position == 3){
            try {
                JSONObject commandData = new JSONObject();
                commandData.put("action", "SYNC");
                commandData.put("subaction", "PUSH");


                JSONArray passwordList = new JSONArray();

                Intent myIntent = getIntent(); // gets the previously created intent
                String username = myIntent.getStringExtra("username");

                List<Password> passwords = db.getUserPasswords(username);

                for(int i = 0; i < passwords.size(); i++){
                    JSONObject password = new JSONObject();

                    password.put("account", passwords.get(i).getAccount());
                    password.put("username", passwords.get(i).getUsername());
                    password.put("password", passwords.get(i).getPassword());
                    passwordList.put(password);
                }


                commandData.put("passwords", passwordList.toString());


                mNetworkTask = new NetworkTask(commandData);
                mNetworkTask.execute((Void) null);


            } catch (JSONException e) {

                e.printStackTrace();

            }
        }
    }



    private ActionBarDrawerToggle mDrawerToggle;
    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        super.onCreateOptionsMenu(menu);
        getMenuInflater().inflate(R.menu.menu_online_main, menu);

        return true;
    }
//    @Override
//    public boolean onPrepareOptionsMenu(Menu menu) {
//        // If the nav drawer is open, hide action items related to the content view
//        boolean drawerOpen = mDrawerLayout.isDrawerOpen(mDrawerList);
//        menu.findItem(R.id.action_websearch).setVisible(!drawerOpen);
//        return super.onPrepareOptionsMenu(menu);
//    }
    public boolean onOptionsItemSelected(MenuItem item) {
        // Pass the event to ActionBarDrawerToggle, if it returns
        // true, then it has handled the app icon touch event
        if (mDrawerToggle.onOptionsItemSelected(item)) {
            return true;
        }

        switch (item.getItemId()) {

            case R.id.action_favorite:
                try {
                    JSONObject commandData = new JSONObject();
                    commandData.put("action", "CRUD");
                    commandData.put("subaction", "READ");

                    mNetworkTask = new NetworkTask(commandData);
                    mNetworkTask.execute((Void) null);


                } catch (JSONException e) {

                    e.printStackTrace();

                }
                return true;

            default:
                // If we got here, the user's action was not recognized.
                // Invoke the superclass to handle it.
                return super.onOptionsItemSelected(item);

        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_online_main);



        String[] mPlanetTitles = { "Password List", "Network Scan" , "Sync:Pull", "Sync:Push", "Logout"};
        mDrawerLayout = (DrawerLayout) findViewById(R.id.drawer_layout);
        mDrawerList = (ListView) findViewById(R.id.left_drawer);

        // Set the adapter for the list view
        mDrawerList.setAdapter(new ArrayAdapter<String>(this,
                R.layout.navitem, mPlanetTitles));
        // Set the list's click listener
        mDrawerList.setOnItemClickListener(new DrawerItemClickListener());



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


        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {


                AlertDialog.Builder builder = new AlertDialog.Builder(OnlineMainActivity.this);
                builder.setTitle("Add New Password");


                // Set up the input
                final EditText input = new EditText(OnlineMainActivity.this);
                input.setInputType(InputType.TYPE_CLASS_TEXT);
                input.setHint("Account");

                final EditText input2 = new EditText(OnlineMainActivity.this);
                input2.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
                input2.setHint("Password");

                LinearLayout ll = new LinearLayout(OnlineMainActivity.this);
                ll.setOrientation(LinearLayout.VERTICAL);
                ll.addView(input);
                ll.addView(input2);
                ll.setPadding(60, 20, 60, 0);
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
                            try {
                                commandData.put("entry", new JSONObject().put("account", account).put("accountPassword", aesCrypt.encrypt_string(password)));
                                mNetworkTask = new NetworkTask(commandData);
                                mNetworkTask.execute((Void) null);
                            }catch (Exception e){
                                System.out.println("Unable to encrypt password");
                            }


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
            String decrypted_password = "";
            // Find the ListView resource.
            mainListView = (ListView) findViewById(R.id.mainListView);
            final Password[] passwords = new Password[passwordList.length()];

            for (int i = 0; i < passwordList.length(); i++) {
                try {
                    decrypted_password = aesCrypt.decrypt_string(passwordList.getJSONObject(i).getString("password"));
                    passwords[i] = new Password(passwordList.getJSONObject(i).getString("account"), decrypted_password, passwordList.getJSONObject(i).getInt("id"));
                }catch (Exception e){
                    passwords[i] = new Password(passwordList.getJSONObject(i).getString("account"), "Unable to Decrypt Password", passwordList.getJSONObject(i).getInt("id"));
                }
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
                            .setIcon(R.drawable.ic_warning_black_48dp)
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

                        if(recvJsonObject.getJSONObject("additional").getString("subaction").equals("CREATE")) {
                            Toast.makeText(getApplicationContext(), "Password Added!", Toast.LENGTH_SHORT).show();
                        }else if(recvJsonObject.getJSONObject("additional").getString("subaction").equals("DELETE")){
                            Toast.makeText(getApplicationContext(), "Password Deleted!", Toast.LENGTH_SHORT).show();
                        }
                    }
                }else if (recvJsonObject.getString("action").equals("SYNC")) {

                    if (recvJsonObject.getJSONObject("additional").getString("subaction").equals("PULL")){
                        Intent myIntent = getIntent(); // gets the previously created intent
                        String username = myIntent.getStringExtra("username");

                        db.deletePasswords(username);
                        final JSONArray passwordList = recvJsonObject.getJSONObject("additional").getJSONArray("passwords");

                        for(int i = 0; i < passwordList.length(); i++){
                            Password p = new Password(passwordList.getJSONObject(i).getString("account"), passwordList.getJSONObject(i).getString("password"), username);
                            db.addPassword(p);
                        }

                        Toast.makeText(getApplicationContext(), "SYNC PULL Complete", Toast.LENGTH_SHORT).show();



                    }else if (recvJsonObject.getJSONObject("additional").getString("subaction").equals("PUSH")){
                        JSONObject commandData = new JSONObject();
                        try {
                            commandData.put("action", "CRUD");
                            commandData.put("subaction", "READ");

                            mNetworkTask = new NetworkTask(commandData);
                            mNetworkTask.execute((Void) null);
                        } catch (JSONException e) {

                            e.printStackTrace();

                        }
                        Toast.makeText(getApplicationContext(), "SYNC PUSH Complete", Toast.LENGTH_SHORT).show();


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
