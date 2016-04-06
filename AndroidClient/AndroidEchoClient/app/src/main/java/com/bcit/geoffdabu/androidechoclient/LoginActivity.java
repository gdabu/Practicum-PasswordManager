package com.bcit.geoffdabu.androidechoclient;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.annotation.TargetApi;

import android.app.AlertDialog;
import android.content.ComponentName;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;

import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.IBinder;
import android.support.annotation.NonNull;
import android.support.design.widget.Snackbar;

import android.support.v7.app.AppCompatActivity;
import android.app.LoaderManager.LoaderCallbacks;

import android.content.CursorLoader;
import android.content.Loader;
import android.database.Cursor;
import android.net.Uri;
import android.os.AsyncTask;

import android.os.Build;
import android.os.Bundle;
import android.provider.ContactsContract;
import android.text.InputType;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.TextPaint;
import android.text.TextUtils;
import android.text.method.LinkMovementMethod;
import android.text.style.ClickableSpan;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.inputmethod.EditorInfo;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;


import java.util.ArrayList;
import java.util.List;

import static android.Manifest.permission.READ_CONTACTS;

/**
 * A login screen that offers login via email/password.
 */
public class LoginActivity extends AppCompatActivity implements LoaderCallbacks<Cursor> {

//    public static final String SERVER_IP = "142.232.169.77"; //your computer IP address
//    public static final int SERVER_PORT = 8000;


    /**
     * Id to identity READ_CONTACTS permission request.
     */
    private static final int REQUEST_READ_CONTACTS = 0;

    /**
     * A dummy authentication store containing known user names and passwords.
     * TODO: remove after connecting to a real authentication system.
     */
//    private static final String[] DUMMY_CREDENTIALS = new String[]{
//            "test@test.com:test", "bar@example.com:world"
//    };
    /**
     * Keep track of the login task to ensure we can cancel it if requested.
     */
    private UserLoginTask mAuthTask = null;

    // UI references.
    private AutoCompleteTextView mEmailView;
    private EditText mPasswordView;
    private View mProgressView;
    private View mLoginFormView;

    private SocketService mBoundService;
    boolean mIsBound = false;

    NetworkTask mNetworkTask = null;

    private ServiceConnection mConnection = new ServiceConnection() {
        //EDITED PART
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            // TODO Auto-generated method stub
            System.out.println("connected");
            mBoundService = ((SocketService.LocalBinder) service).getService();
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            // TODO Auto-generated method stub
            mBoundService = null;
        }

    };

    private void doBindService() {
        bindService(new Intent(LoginActivity.this, SocketService.class), mConnection, Context.BIND_AUTO_CREATE);
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        // Set up the login form.
        mEmailView = (AutoCompleteTextView) findViewById(R.id.email);
        populateAutoComplete();


        mPasswordView = (EditText) findViewById(R.id.password);
        mPasswordView.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView textView, int id, KeyEvent keyEvent) {
                if (id == R.id.login || id == EditorInfo.IME_NULL) {
                    attemptLogin();
                    return true;
                }
                return false;
            }
        });

        Button mEmailSignInButton = (Button) findViewById(R.id.email_sign_in_button);
        mEmailSignInButton.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View view) {
                attemptLogin();
            }
        });

        mLoginFormView = findViewById(R.id.login_form);
        mProgressView = findViewById(R.id.login_progress);

        SpannableString ss = new SpannableString("Create one.");
        ClickableSpan clickableSpan = new ClickableSpan() {
            @Override
            public void onClick(View textView) {
//                startActivity(new Intent(LoginActivity.this, LoginActivity.class));
                if (mBoundService.isConnected()) {

//                builder.setMessage("A secret key was sent to your email");
                    // Set up the input
                    final EditText input = new EditText(LoginActivity.this);
                    final EditText input2 = new EditText(LoginActivity.this);
                    final EditText input3 = new EditText(LoginActivity.this);
                    input.setInputType(InputType.TYPE_CLASS_TEXT);
                    input.setHint("User Name");
                    input2.setInputType(InputType.TYPE_CLASS_TEXT |
                            InputType.TYPE_TEXT_VARIATION_PASSWORD);
                    input2.setHint("Password");
                    input3.setInputType(InputType.TYPE_CLASS_TEXT |
                            InputType.TYPE_TEXT_VARIATION_PASSWORD);
                    input3.setHint("Confirm Password");


                    LinearLayout ll = new LinearLayout(LoginActivity.this);
                    ll.setOrientation(LinearLayout.VERTICAL);
                    ll.addView(input);
                    ll.addView(input2);
                    ll.addView(input3);
                    ll.setPadding(60, 20, 60, 0);

                    final AlertDialog d = new AlertDialog.Builder(LoginActivity.this)
                            .setTitle("Sign Up")
                            .setView(ll)
                            .setPositiveButton(android.R.string.ok, null)
                            .setNegativeButton(android.R.string.cancel, null)
                            .create();

                    d.setOnShowListener(new DialogInterface.OnShowListener() {

                        @Override
                        public void onShow(DialogInterface dialog) {

                            Button b = d.getButton(AlertDialog.BUTTON_POSITIVE);
                            b.setOnClickListener(new View.OnClickListener() {

                                @Override
                                public void onClick(View view) {
                                    // TODO Do something

                                    //Dismiss once everything is OK.
                                    String username = input.getText().toString();
                                    String password = input2.getText().toString();
                                    String confirmpassword = input3.getText().toString();


                                    if (!password.equals(confirmpassword)) {
                                        Toast toast = Toast.makeText(getApplicationContext(), "Password does not match", Toast.LENGTH_SHORT);
                                        toast.show();
                                        return;
                                    }

                                    JSONObject commandData = new JSONObject();
                                    try {

                                        commandData.put("action", "REGISTER");
                                        commandData.put("username", username);
                                        commandData.put("password", password);

                                        mNetworkTask = new NetworkTask(commandData);
                                        mNetworkTask.execute((Void) null);
                                        d.dismiss();

                                    } catch (JSONException e) {
                                        e.printStackTrace();
                                    }

                                }
                            });
                        }
                    });

                    d.show();
                } else {
                    Toast toast = Toast.makeText(getApplicationContext(), "No Connection", Toast.LENGTH_SHORT);
                    toast.show();

                }

            }

            @Override
            public void updateDrawState(TextPaint ds) {
                super.updateDrawState(ds);
                ds.setUnderlineText(false);
            }
        };
        ss.setSpan(clickableSpan, 0, ss.length() - 1, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);

        TextView textView = (TextView) findViewById(R.id.registerLink);
        textView.append(ss);
        textView.setMovementMethod(LinkMovementMethod.getInstance());
        textView.setHighlightColor(Color.TRANSPARENT);


        startService(new Intent(this, SocketService.class));
        doBindService();


    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopService(new Intent(this, SocketService.class));
        doUnbindService();

    }

    private void populateAutoComplete() {
        if (!mayRequestContacts()) {
            return;
        }

        getLoaderManager().initLoader(0, null, this);
    }

    private boolean mayRequestContacts() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
            return true;
        }
        if (checkSelfPermission(READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            return true;
        }
        if (shouldShowRequestPermissionRationale(READ_CONTACTS)) {
            Snackbar.make(mEmailView, R.string.permission_rationale, Snackbar.LENGTH_INDEFINITE)
                    .setAction(android.R.string.ok, new View.OnClickListener() {
                        @Override
                        @TargetApi(Build.VERSION_CODES.M)
                        public void onClick(View v) {
                            requestPermissions(new String[]{READ_CONTACTS}, REQUEST_READ_CONTACTS);
                        }
                    });
        } else {
            requestPermissions(new String[]{READ_CONTACTS}, REQUEST_READ_CONTACTS);
        }
        return false;
    }

    /**
     * Callback received when a permissions request has been completed.
     */
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        if (requestCode == REQUEST_READ_CONTACTS) {
            if (grantResults.length == 1 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                populateAutoComplete();
            }
        }
    }


    /**
     * Attempts to sign in or register the account specified by the login form.
     * If there are form errors (invalid email, missing fields, etc.), the
     * errors are presented and no actual login attempt is made.
     */
    private void attemptLogin() {
        if (mAuthTask != null) {
            return;
        }

        // Reset errors.
        mEmailView.setError(null);
        mPasswordView.setError(null);

        // Store values at the time of the login attempt.
        String email = mEmailView.getText().toString();
        String password = mPasswordView.getText().toString();

        boolean cancel = false;
        View focusView = null;

        // Check for a valid password, if the user entered one.
        if (!TextUtils.isEmpty(password) && !isPasswordValid(password)) {
            mPasswordView.setError(getString(R.string.error_invalid_password));
            focusView = mPasswordView;
            cancel = true;
        }

        // Check for a valid email address.
        if (TextUtils.isEmpty(email)) {
            mEmailView.setError(getString(R.string.error_field_required));
            focusView = mEmailView;
            cancel = true;
        } else if (!isEmailValid(email)) {
            mEmailView.setError(getString(R.string.error_invalid_email));
            focusView = mEmailView;
            cancel = true;
        }

        if (cancel) {
            // There was an error; don't attempt login and focus the first
            // form field with an error.
            focusView.requestFocus();
        } else {
            // Show a progress spinner, and kick off a background task to
            // perform the user login attempt.
            showProgress(true);
            mAuthTask = new UserLoginTask(email, password);
            mAuthTask.execute((Void) null);
        }
    }

    private boolean isEmailValid(String email) {
        //TODO: Replace this with your own logic
        return email.contains("@");
    }

    private boolean isPasswordValid(String password) {
        //TODO: Replace this with your own logic
        return password.length() > 0;
    }

    /**
     * Shows the progress UI and hides the login form.
     */
    @TargetApi(Build.VERSION_CODES.HONEYCOMB_MR2)
    private void showProgress(final boolean show) {
        // On Honeycomb MR2 we have the ViewPropertyAnimator APIs, which allow
        // for very easy animations. If available, use these APIs to fade-in
        // the progress spinner.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB_MR2) {
            int shortAnimTime = getResources().getInteger(android.R.integer.config_shortAnimTime);

            mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
            mLoginFormView.animate().setDuration(shortAnimTime).alpha(
                    show ? 0 : 1).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
                }
            });

            mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
            mProgressView.animate().setDuration(shortAnimTime).alpha(
                    show ? 1 : 0).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
                }
            });
        } else {
            // The ViewPropertyAnimator APIs are not available, so simply show
            // and hide the relevant UI components.
            mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
            mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
        }
    }

    @Override
    public Loader<Cursor> onCreateLoader(int i, Bundle bundle) {
        return new CursorLoader(this,
                // Retrieve data rows for the device user's 'profile' contact.
                Uri.withAppendedPath(ContactsContract.Profile.CONTENT_URI,
                        ContactsContract.Contacts.Data.CONTENT_DIRECTORY), ProfileQuery.PROJECTION,

                // Select only email addresses.
                ContactsContract.Contacts.Data.MIMETYPE +
                        " = ?", new String[]{ContactsContract.CommonDataKinds.Email
                .CONTENT_ITEM_TYPE},

                // Show primary email addresses first. Note that there won't be
                // a primary email address if the user hasn't specified one.
                ContactsContract.Contacts.Data.IS_PRIMARY + " DESC");
    }

    @Override
    public void onLoadFinished(Loader<Cursor> cursorLoader, Cursor cursor) {
        List<String> emails = new ArrayList<>();
        cursor.moveToFirst();
        while (!cursor.isAfterLast()) {
            emails.add(cursor.getString(ProfileQuery.ADDRESS));
            cursor.moveToNext();
        }

        addEmailsToAutoComplete(emails);
    }

    @Override
    public void onLoaderReset(Loader<Cursor> cursorLoader) {

    }

    private void addEmailsToAutoComplete(List<String> emailAddressCollection) {
        //Create adapter to tell the AutoCompleteTextView what to show in its dropdown list.
        ArrayAdapter<String> adapter =
                new ArrayAdapter<>(LoginActivity.this,
                        android.R.layout.simple_dropdown_item_1line, emailAddressCollection);

        mEmailView.setAdapter(adapter);
    }


    private interface ProfileQuery {
        String[] PROJECTION = {
                ContactsContract.CommonDataKinds.Email.ADDRESS,
                ContactsContract.CommonDataKinds.Email.IS_PRIMARY,
        };

        int ADDRESS = 0;
        int IS_PRIMARY = 1;
    }


    /**
     * Represents an asynchronous login/registration task used to authenticate
     * the user.
     */
    public class UserLoginTask extends AsyncTask<Void, Void, Boolean> {

        private final String mEmail;
        private final String mPassword;

        private String loginStatus;

        UserLoginTask(String email, String password) {
            mEmail = email;
            mPassword = password;
        }

        @Override
        protected Boolean doInBackground(Void... params) {

            JSONObject login = new JSONObject();
            JSONObject recvJsonData = new JSONObject();

            try {

                login.put("action", "LOGIN");
                login.put("username", mEmail);
                login.put("password", mPassword);

                if (mBoundService.isConnected()) {

                    if (mBoundService != null) {
                        recvJsonData = mBoundService.sendMessage(login.toString());
                    }

                    if (recvJsonData.getString("action").equals("LOGIN") && recvJsonData.getInt("status") == 200) {


                        if (recvJsonData.getJSONObject("additional").getBoolean("tfa_enabled") == false) {
                            Log.e("TCP Client", "Successful User Login");

                            loginStatus = "success";
                            return true;
                        } else {
//                          // TODO: PROMPT WITH 2FA KEY MENU
                            loginStatus = "fail_need2fa";
                            return false;
                        }


                    } else {
                        Log.e("TCP Client", "Unsuccessful User Login");
                        loginStatus = "fail_wrongPassword";
                        return false;
                    }

                } else {
                    System.out.println("Unable to Connect");
                    loginStatus = "fail_noConnection";
                    return false;
                }

            } catch (JSONException e) {

                System.out.print("Login Error: ");
                e.printStackTrace();

            }

            return false;
        }


        @Override
        protected void onPostExecute(final Boolean success) {
            mAuthTask = null;
            showProgress(false);

            if (success) {
                // Switching to Register screen
                Intent i = new Intent(getApplicationContext(), OnlineMainActivity.class);
                startActivity(i);
//                finish();

            } else {

                if (loginStatus.equals("fail_need2fa")) {


                    AlertDialog.Builder builder = new AlertDialog.Builder(LoginActivity.this);
                    builder.setTitle("Enter 2FA Key");
                    builder.setMessage("A secret key was sent to your email");
                    // Set up the input
                    final EditText input = new EditText(LoginActivity.this);
                    input.setInputType(InputType.TYPE_CLASS_TEXT);
                    input.setHint("Enter Secret Key: ");


                    LinearLayout ll = new LinearLayout(LoginActivity.this);
                    ll.setOrientation(LinearLayout.VERTICAL);
                    ll.addView(input);
                    ll.setPadding(60, 20, 60, 0);
                    builder.setView(ll);

                    // Set up the buttons
                    builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            String secret = input.getText().toString();
                            JSONObject commandData = new JSONObject();
                            try {
                                commandData.put("action", "2FA_LOGIN");
                                commandData.put("secret", secret);

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

                } else if (loginStatus.equals("fail_wrongPassword")) {

                    mPasswordView.setError(getString(R.string.error_incorrect_password));
                    mPasswordView.requestFocus();

                } else if ((loginStatus.equals("fail_noConnection"))) {

                    Toast toast = Toast.makeText(getApplicationContext(), "No Connection", Toast.LENGTH_SHORT);
                    toast.show();

                } else {

                }
            }
        }

        @Override
        protected void onCancelled() {
            mAuthTask = null;
            showProgress(false);
        }

    }

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


                if (recvJsonObject.getString("action").equals("2FA_LOGIN")) {
                    if (recvJsonObject.getInt("status") == 200) {
                        Intent i = new Intent(getApplicationContext(), OnlineMainActivity.class);
                        startActivity(i);

                    } else {

                        Toast toast = Toast.makeText(LoginActivity.this, "Incorrect Secret Key", Toast.LENGTH_SHORT);
                        toast.show();
                    }
                } else if (recvJsonObject.getString("action").equals("REGISTER")) {
                    if (recvJsonObject.getInt("status") == 200) {
                        Toast toast = Toast.makeText(LoginActivity.this, "Registration Successful", Toast.LENGTH_SHORT);
                        toast.show();
                    } if(recvJsonObject.getInt("status") == 401) {
                        Toast toast = Toast.makeText(LoginActivity.this, "Username Taken", Toast.LENGTH_SHORT);
                        toast.show();
                    }else {
                        Toast toast = Toast.makeText(LoginActivity.this, "Registration Unsuccessful", Toast.LENGTH_SHORT);
                        toast.show();
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

