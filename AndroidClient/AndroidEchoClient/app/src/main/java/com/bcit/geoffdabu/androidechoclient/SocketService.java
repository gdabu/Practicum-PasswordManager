package com.bcit.geoffdabu.androidechoclient;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import android.widget.Toast;

public class SocketService extends Service {
    public static final String SERVERIP = "192.168.0.8"; //your computer IP address should be written here
    public static final int SERVERPORT = 8000;
    PrintWriter out;
    BufferedReader in;
    Socket socket;
    InetAddress serverAddr;

    @Override
    public IBinder onBind(Intent intent) {
        // TODO Auto-generated method stub
        System.out.println("I am in Ibinder onBind method");
        return myBinder;
    }

    private final IBinder myBinder = new LocalBinder();
//    TCPClient mTcpClient = new TCPClient();

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

    public void IsBoundable(){
        Toast.makeText(this,"I bind like butter", Toast.LENGTH_LONG).show();
    }

    public void sendMessage(String message){
        try{
        if (out != null && !out.checkError()) {
            System.out.println("in sendMessage"+message);
            out.println(message);
            out.flush();


            String response = in.readLine();
            System.out.println("fuckeroni: " + response);
        }
        }catch(Exception e){
            System.out.println("disconnected");
        }

    }

    @Override
    public int onStartCommand(Intent intent,int flags, int startId){
        super.onStartCommand(intent, flags, startId);
        System.out.println("I am in on start");
        //  Toast.makeText(this,"Service created ...", Toast.LENGTH_LONG).show();
        Runnable connect = new connectSocket();
        new Thread(connect).start();
        return START_STICKY;
    }


    class connectSocket implements Runnable {

        @Override
        public void run() {


            try {
                //here you must put your computer's IP address.
                serverAddr = InetAddress.getByName(SERVERIP);
                Log.e("TCP Client", "C: Connecting...");
                //create a socket to make the connection with the server

                socket = new Socket(serverAddr, SERVERPORT);

                try {


                    //send the message to the server
                    out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);


                    Log.e("TCP Client", "C: Sent.");

                    Log.e("TCP Client", "C: Done.");
                    in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                }
                catch (Exception e) {

                    Log.e("TCP", "S: Error", e);

                }
            } catch (Exception e) {

                Log.e("TCP", "C: Error", e);

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