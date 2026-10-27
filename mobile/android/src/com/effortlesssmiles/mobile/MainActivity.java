package com.effortlesssmiles.mobile;
import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.content.ActivityNotFoundException;
import android.net.Uri;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.View;
import android.widget.*;
public class MainActivity extends Activity {
 private static final String HOME="https://effortless-smiles-studio.hazy-tern-4233.chatgpt.site";
 private LinearLayout content;
 private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density);}
 private TextView text(String value,int size,int color){TextView v=new TextView(this);v.setText(value);v.setTextSize(size);v.setTextColor(color);v.setPadding(0,dp(8),0,dp(8));return v;}
 private void open(String path){String url=path.startsWith("https://")?path:HOME+path;Uri uri=Uri.parse(url);if(!"https".equals(uri.getScheme()))return;try{Intent i=new Intent(Intent.ACTION_VIEW,uri);i.addCategory(Intent.CATEGORY_BROWSABLE);Bundle extra=new Bundle();extra.putBinder("android.support.customtabs.extra.SESSION",null);i.putExtras(extra);i.putExtra("android.support.customtabs.extra.TOOLBAR_COLOR",Color.rgb(48,32,57));startActivity(i);}catch(ActivityNotFoundException e){Toast.makeText(this,"Install or enable a browser to open the platform.",Toast.LENGTH_LONG).show();}}
 private void button(String label,final String path){Button b=new Button(this);b.setText(label);b.setAllCaps(false);b.setTextColor(Color.WHITE);b.setTextSize(15);GradientDrawable bg=new GradientDrawable();bg.setColor(Color.rgb(59,37,72));bg.setCornerRadius(dp(9));b.setBackground(bg);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(53));p.setMargins(0,dp(7),0,dp(7));content.addView(b,p);b.setOnClickListener(new View.OnClickListener(){public void onClick(View v){open(path);}});}
 @Override public void onCreate(Bundle state){super.onCreate(state);getWindow().setStatusBarColor(Color.rgb(48,32,57));getWindow().setNavigationBarColor(Color.rgb(48,32,57));ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(Color.rgb(252,250,247));content=new LinearLayout(this);content.setOrientation(LinearLayout.VERTICAL);content.setPadding(dp(25),dp(34),dp(25),dp(36));scroll.addView(content);setContentView(scroll);ImageView art=new ImageView(this);int artId=getResources().getIdentifier("brand_artwork","drawable",getPackageName());art.setImageResource(artId);art.setScaleType(ImageView.ScaleType.CENTER_CROP);art.setContentDescription("Effortless Smiles purple crystal brand artwork");content.addView(art,new LinearLayout.LayoutParams(-1,dp(190)));TextView title=text("Effortless Smiles",30,Color.rgb(48,32,57));title.setTypeface(Typeface.SERIF);content.addView(title);content.addView(text("Your smile. Your signature sparkle.",17,Color.rgb(118,83,134)));content.addView(text("Your studio, appointments and smile shop — with your normal browser sign-in.",14,Color.rgb(119,105,128)));button("Open my platform","/");button("Customer demo","/demo?role=customer");button("Staff demo","/demo?role=staff");button("Super admin demo","/demo?role=super_admin");button("Install & update information","/install");button("African Apps Store","https://africanappsstore.space/");content.addView(text("DEMO SAFETY\nSample records only. Demos cannot make live payments or purchases. Each role has its own allowed features.",13,Color.rgb(118,83,134)));content.addView(text("Development preview 0.1.0 · Android 8+\nThis companion opens the web platform in a browser tab. Internet and platform access are required. No offline bookings, native push notifications or background services. Not a Google Play release.",12,Color.rgb(129,117,138)));}
}
