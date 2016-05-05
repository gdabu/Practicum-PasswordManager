package com.bcit.geoffdabu.androidechoclient;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ConnectException;
import java.net.InetAddress;
import java.net.Socket;
import java.security.GeneralSecurityException;
import java.security.KeyManagementException;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;

import android.util.Log;
import android.widget.Toast;

import org.json.JSONObject;

import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManagerFactory;

public class SocketService extends Service {
    public static final String SERVERIP = "192.168.0.9"; //your computer IP address should be written here
    public static final int SERVERPORT = 8000;

    private PrintWriter out;
    private BufferedReader in;
    private Socket socket = null;
    private InetAddress serverAddr;

    public boolean isConnected(){
        if(socket == null){
            return false;
        }
        return true;
    }

    @Override
    public IBinder onBind(Intent intent) {
        // TODO Auto-generated method stub
        System.out.println("I am in Ibinder onBind method");
        return myBinder;
    }

    private final IBinder myBinder = new LocalBinder();

    public class LocalBinder extends Binder {
        public SocketService getService() {
            System.out.println("I am in Localbinder ");
            return SocketService.this;
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();
        System.out.println("I am in on create");
    }

    public void IsBoundable() {

    }

    public JSONObject sendMessage(String message) {
        JSONObject response = null;

        try {
            if (out != null && !out.checkError()) {

                System.out.println("in sendMessage" + message);
                out.println(message);
                out.flush();

                response = new JSONObject(in.readLine());
            }
        } catch (Exception e) {
            System.out.println("disconnected");
        }

        return response;

    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        System.out.println("I am in on start");
        //  Toast.makeText(this,"Service created ...", Toast.LENGTH_LONG).show();
        Runnable connect = new connectSocket();
        new Thread(connect).start();
        return START_STICKY;
    }

    private Socket getConnection(String ip, int port) throws IOException, KeyStoreException, CertificateException, NoSuchAlgorithmException, KeyManagementException {

            KeyStore trustStore = KeyStore.getInstance("BKS");

            InputStream trustStoreStream = this.getResources().openRawResource(R.raw.server);
            trustStore.load(trustStoreStream, "keypass".toCharArray());

            TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStore);

            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(null, trustManagerFactory.getTrustManagers(), null);
            SSLSocketFactory factory = sslContext.getSocketFactory();
            SSLSocket socket = (SSLSocket) factory.createSocket(ip, port);
            return socket;
    }


    class connectSocket implements Runnable {

        @Override
        public void run() {


            try {
                //here you must put your computer's IP address.
                serverAddr = InetAddress.getByName(SERVERIP);
                Log.e("TCP Client", "C: Connecting...");
                //create a socket to make the connection with the server

//                socket = new Socket(serverAddr, SERVERPORT);
                socket = getConnection(SERVERIP, SERVERPORT);
                try {


                    //send the message to the server
                    out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);


                    Log.e("TCP Client", "C: Sent.");

                    Log.e("TCP Client", "C: Done.");
                    in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                } catch (Exception e) {

                    Log.e("TCP", "S: Error", e);
                    onDestroy();

                }
            } catch (Exception e) {

                Log.e("TCP", "C: Error", e);
                onDestroy();

            }

        }

    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        try {
            socket.close();
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        socket = null;
    }


}