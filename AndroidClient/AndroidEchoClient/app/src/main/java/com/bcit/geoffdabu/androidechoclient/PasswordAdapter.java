//package com.bcit.geoffdabu.androidechoclient;
//
//import android.app.Activity;
//import android.content.Context;
//import android.view.LayoutInflater;
//import android.view.View;
//import android.view.ViewGroup;
//import android.widget.ArrayAdapter;
//import android.widget.BaseAdapter;
//import android.widget.RelativeLayout;
//import android.widget.TextView;
//
//import java.util.ArrayList;
//import java.util.List;
//
///**
// * Created by geoffdabu on 2016-04-03.
// */
//public class PasswordAdapter extends BaseAdapter {
//    private List<Password> items;
//    private Context context;
//    private int numItems = 0;
//
//    public PasswordAdapter(final List<Password> items, Context context) {
//        this.items = items;
//        this.context = context;
//        this.numItems = items.size();
//    }
//
//    public int getCount() {
//        return numItems;
//    }
//
//    public Password getItem(int position) {
//        return items.get(position);
//    }
//
//    public long getItemId(int position) {
//        return 0;
//    }
//
//    public View getView(int position, View convertView, ViewGroup parent) {
//
//        // Get the current list item
//        final Password item = items.get(position);
//        // Get the layout for the list item
//        final TextView itemLayout = (TextView) LayoutInflater.from(context).inflate(R.layout.listitem, parent, false);
//        // Set the icon as defined in our list item
//
//
//
//        // Set the text label as defined in our list item
//        TextView txtLabel = (TextView) itemLayout.findViewById(R.id.rowTextView);
//        txtLabel.setText(item.getAccount());
//
//        return itemLayout;
//    }
//}