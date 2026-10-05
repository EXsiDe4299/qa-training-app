package com.example.qatrainingapp;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.List;

public class MainActivity extends android.app.Activity {
    private static final String DEFAULT_API_URL = "http://10.0.2.2:8000";
    private static final String PREFS = "qa_training_prefs";
    private static final String PREF_API_URL = "api_url";

    private LinearLayout root;
    private TextView status;
    private ApiClient api;
    private SharedPreferences prefs;
    private String currentUsername = "";

    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String apiUrl = prefs.getString(PREF_API_URL, DEFAULT_API_URL);
        api = new ApiClient(apiUrl);
        showLogin();
    }

    @Override
    protected void onDestroy() {
        api.shutdown();
        super.onDestroy();
    }

    private void setupRoot(String screenId, String title) {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(0xFFF7F7FA);
        root.setPadding(dp(20), dp(20), dp(20), dp(20));
        root.setContentDescription(screenId);
        root.setId(getResources().getIdentifier(screenId, "id", getPackageName()));

        TextView titleView = new TextView(this);
        titleView.setText(title);
        titleView.setTextSize(26);
        titleView.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        titleView.setTextColor(0xFF202124);
        titleView.setPadding(0, 0, 0, dp(16));
        root.addView(titleView, matchWrap());

        status = new TextView(this);
        status.setId(R.id.text_status);
        status.setTextSize(14);
        status.setTextColor(0xFF5F6368);
        status.setPadding(0, 0, 0, dp(10));
        status.setVisibility(View.GONE);
        root.addView(status, matchWrap());

        setContentView(root);
    }

    private LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private LinearLayout.LayoutParams matchWeight() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0);
        lp.weight = 1;
        return lp;
    }

    private TextView label(String text) {
        TextView v = new TextView(this);
        v.setText(text);
        v.setTextSize(14);
        v.setTextColor(0xFF3C4043);
        v.setPadding(0, dp(8), 0, dp(4));
        return v;
    }

    private EditText input(int id, String hint, boolean password) {
        EditText edit = new EditText(this);
        edit.setId(id);
        edit.setHint(hint);
        edit.setTextSize(16);
        edit.setSingleLine(!hint.toLowerCase().contains("description"));
        edit.setPadding(dp(12), dp(8), dp(12), dp(8));
        if (password) {
            edit.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        } else {
            edit.setInputType(InputType.TYPE_CLASS_TEXT);
        }
        LinearLayout.LayoutParams lp = matchWrap();
        lp.bottomMargin = dp(4);
        root.addView(edit, lp);
        return edit;
    }

    private Button button(int id, String text) {
        Button button = new Button(this);
        button.setId(id);
        button.setText(text);
        button.setAllCaps(false);
        button.setMinHeight(dp(48));
        button.setContentDescription(text);
        LinearLayout.LayoutParams lp = matchWrap();
        lp.topMargin = dp(6);
        root.addView(button, lp);
        return button;
    }

    private void setStatus(String message) {
        status.setText(message);
        status.setVisibility(View.VISIBLE);
    }

    private void clearStatus() {
        status.setVisibility(View.GONE);
        status.setText("");
    }

    private String apiUrl() {
        return prefs.getString(PREF_API_URL, DEFAULT_API_URL);
    }

    private void showLogin() {
        setupRoot("screen_login", "QA Training App");
        clearStatus();

        TextView subtitle = new TextView(this);
        subtitle.setText("Login to the training API");
        subtitle.setTextSize(16);
        subtitle.setTextColor(0xFF5F6368);
        root.addView(subtitle, matchWrap());

        root.addView(label("Username"), matchWrap());
        EditText username = input(R.id.input_login_username, "Username", false);
        root.addView(label("Password"), matchWrap());
        EditText password = input(R.id.input_login_password, "Password", true);

        Button login = button(R.id.button_login, "Login");
        Button register = button(R.id.button_open_register, "Create account");
        Button settings = button(R.id.button_open_settings, "API settings");

        TextView endpoint = new TextView(this);
        endpoint.setText("API: " + apiUrl());
        endpoint.setTextSize(12);
        endpoint.setTextColor(0xFF6B7280);
        endpoint.setPadding(0, dp(12), 0, dp(0));
        root.addView(endpoint, matchWrap());

        login.setOnClickListener(v -> {
            String u = username.getText().toString().trim();
            String p = password.getText().toString();
            if (u.isEmpty() || p.isEmpty()) {
                setStatus("Username and password are required.");
                return;
            }
            setStatus("Logging in…");
            api.setBaseUrl(apiUrl());
            api.login(u, p, new ApiClient.Callback<ApiClient.LoginResult>() {
                @Override
                public void onSuccess(ApiClient.LoginResult result) {
                    currentUsername = result.username;
                    setStatus("Login successful.");
                    showRequests();
                }

                @Override
                public void onError(String message) {
                    setStatus(message);
                }
            });
        });

        register.setOnClickListener(v -> showRegister());
        settings.setOnClickListener(v -> showSettings());
    }

    private void showRegister() {
        setupRoot("screen_register", "Create account");
        clearStatus();

        root.addView(label("Username"), matchWrap());
        EditText username = input(R.id.input_register_username, "Username", false);
        root.addView(label("Password"), matchWrap());
        EditText password = input(R.id.input_register_password, "Password", true);
        root.addView(label("Repeat password"), matchWrap());
        EditText confirm = input(R.id.input_register_password_confirm, "Repeat password", true);

        Button register = button(R.id.button_register, "Register");
        Button back = button(R.id.button_back_login, "Back to login");

        register.setOnClickListener(v -> {
            String u = username.getText().toString().trim();
            String p = password.getText().toString();
            String p2 = confirm.getText().toString();
            if (u.isEmpty() || p.isEmpty() || p2.isEmpty()) {
                setStatus("All fields are required.");
                return;
            }
            if (!p.equals(p2)) {
                setStatus("Passwords do not match.");
                return;
            }
            setStatus("Creating account…");
            api.setBaseUrl(apiUrl());
            api.register(u, p, new ApiClient.Callback<ApiClient.User>() {
                @Override
                public void onSuccess(ApiClient.User result) {
                    Toast.makeText(MainActivity.this, "Account created", Toast.LENGTH_SHORT).show();
                    showLogin();
                    setStatus("Account created. Log in with the new account.");
                }

                @Override
                public void onError(String message) {
                    setStatus(message);
                }
            });
        });
        back.setOnClickListener(v -> showLogin());
    }

    private void showSettings() {
        setupRoot("screen_settings", "API settings");
        clearStatus();

        root.addView(label("API base URL"), matchWrap());
        EditText apiInput = input(R.id.input_api_url, "http://10.0.2.2:8000", false);
        apiInput.setText(apiUrl());
        apiInput.setSelectAllOnFocus(true);

        TextView hint = new TextView(this);
        hint.setText("Emulator → host PC: 10.0.2.2. Physical phone: use your PC's LAN IP, for example 192.168.1.10.");
        hint.setTextSize(12);
        hint.setTextColor(0xFF6B7280);
        hint.setPadding(0, dp(8), 0, dp(8));
        root.addView(hint, matchWrap());

        Button save = button(R.id.button_save_settings, "Save");
        Button reset = button(R.id.button_reset_settings, "Reset to emulator default");
        Button back = button(R.id.button_settings_back, "Back");

        save.setOnClickListener(v -> {
            String value = apiInput.getText().toString().trim();
            if (value.isEmpty()) {
                setStatus("API URL cannot be empty.");
                return;
            }
            prefs.edit().putString(PREF_API_URL, value).apply();
            api.setBaseUrl(value);
            setStatus("Saved: " + value);
        });

        reset.setOnClickListener(v -> {
            prefs.edit().putString(PREF_API_URL, DEFAULT_API_URL).apply();
            api.setBaseUrl(DEFAULT_API_URL);
            apiInput.setText(DEFAULT_API_URL);
            setStatus("Reset to " + DEFAULT_API_URL);
        });

        back.setOnClickListener(v -> showLogin());
    }

    private void showRequests() {
        setupRoot("screen_requests", "Requests");

        LinearLayout topRow = new LinearLayout(this);
        topRow.setOrientation(LinearLayout.HORIZONTAL);
        topRow.setGravity(Gravity.CENTER_VERTICAL);
        root.addView(topRow, matchWrap());

        TextView user = new TextView(this);
        user.setText("Logged in as: " + (currentUsername.isEmpty() ? "unknown" : currentUsername));
        user.setTextSize(15);
        user.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        LinearLayout.LayoutParams userLp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1);
        topRow.addView(user, userLp);

        Button profile = new Button(this);
        profile.setId(R.id.button_profile);
        profile.setText("Me");
        profile.setAllCaps(false);
        profile.setContentDescription("Profile");
        topRow.addView(profile, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button logout = new Button(this);
        logout.setId(R.id.button_logout);
        logout.setText("Logout");
        logout.setAllCaps(false);
        logout.setContentDescription("Logout");
        topRow.addView(logout, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        root.addView(label("Create request"), matchWrap());
        EditText title = input(R.id.input_request_title, "Title", false);
        root.addView(label("Description"), matchWrap());
        EditText description = input(R.id.input_request_description, "Description", false);
        description.setSingleLine(false);
        description.setMinLines(3);
        description.setGravity(Gravity.TOP | Gravity.START);

        Button create = button(R.id.button_create_request, "Create request");
        Button refresh = button(R.id.button_refresh_requests, "Refresh list");

        TextView listHeader = new TextView(this);
        listHeader.setText("Existing requests");
        listHeader.setTextSize(18);
        listHeader.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        listHeader.setPadding(0, dp(14), 0, dp(8));
        root.addView(listHeader, matchWrap());

        ScrollView scroll = new ScrollView(this);
        LinearLayout list = new LinearLayout(this);
        list.setId(R.id.list_requests);
        list.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(list, matchWrap());
        LinearLayout.LayoutParams scrollLp = matchWeight();
        scrollLp.topMargin = dp(2);
        root.addView(scroll, scrollLp);

        create.setOnClickListener(v -> {
            String t = title.getText().toString().trim();
            String d = description.getText().toString().trim();
            if (t.isEmpty() || d.isEmpty()) {
                setStatus("Title and description are required.");
                return;
            }
            setStatus("Creating request…");
            api.createRequest(t, d, new ApiClient.Callback<ApiClient.RequestItem>() {
                @Override
                public void onSuccess(ApiClient.RequestItem result) {
                    title.setText("");
                    description.setText("");
                    setStatus("Created request #" + result.id + ".");
                    loadRequests(list);
                }

                @Override
                public void onError(String message) {
                    setStatus(message);
                }
            });
        });

        refresh.setOnClickListener(v -> loadRequests(list));
        profile.setOnClickListener(v -> {
            setStatus("Loading profile…");
            api.me(new ApiClient.Callback<ApiClient.User>() {
                @Override
                public void onSuccess(ApiClient.User result) {
                    currentUsername = result.username;
                    setStatus("/auth/me → id=" + result.id + ", username=" + result.username);
                }

                @Override
                public void onError(String message) {
                    setStatus(message);
                }
            });
        });

        logout.setOnClickListener(v -> {
            setStatus("Logging out…");
            api.logout(new ApiClient.Callback<String>() {
                @Override
                public void onSuccess(String result) {
                    currentUsername = "";
                    showLogin();
                    setStatus(result);
                }

                @Override
                public void onError(String message) {
                    // Clear the client-side cookie even when the API responds with an error.
                    api.clearCookies();
                    currentUsername = "";
                    showLogin();
                    setStatus("Logout error: " + message);
                }
            });
        });

        loadRequests(list);
    }

    private void loadRequests(LinearLayout list) {
        setStatus("Loading requests…");
        api.getRequests(new ApiClient.Callback<List<ApiClient.RequestItem>>() {
            @Override
            public void onSuccess(List<ApiClient.RequestItem> requests) {
                list.removeAllViews();
                if (requests.isEmpty()) {
                    TextView empty = new TextView(MainActivity.this);
                    empty.setId(R.id.text_empty_requests);
                    empty.setText("No requests yet.");
                    empty.setTextSize(15);
                    empty.setTextColor(0xFF6B7280);
                    list.addView(empty, matchWrap());
                } else {
                    for (ApiClient.RequestItem request : requests) {
                        addRequestCard(list, request);
                    }
                }
                clearStatus();
            }

            @Override
            public void onError(String message) {
                setStatus(message);
            }
        });
    }

    private void showRequestDetails(ApiClient.RequestItem request) {
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Request #" + request.id)
                .setMessage(
                        "Title: " + request.title +
                        "\n\nDescription: " + request.description +
                        "\n\nAuthor: " + request.authorUsername + " (id " + request.authorId + ")"
                )
                .setPositiveButton("Close", null)
                .create();

        dialog.setOnShowListener(ignored -> {
            Button close = dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE);
            close.setId(R.id.button_close_details);
            close.setContentDescription("Close details");
        });
        dialog.show();
    }

    private void addRequestCard(LinearLayout list, ApiClient.RequestItem request) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(14), dp(12), dp(14), dp(12));
        card.setBackgroundColor(0xFFFFFFFF);
        card.setContentDescription("Request #" + request.id);
        LinearLayout.LayoutParams cardLp = matchWrap();
        cardLp.bottomMargin = dp(8);
        list.addView(card, cardLp);

        TextView title = new TextView(this);
        title.setText("#" + request.id + "  " + request.title);
        title.setTextSize(17);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        card.addView(title, matchWrap());

        TextView description = new TextView(this);
        description.setText(request.description);
        description.setTextSize(15);
        description.setTextColor(0xFF3C4043);
        description.setPadding(0, dp(6), 0, dp(6));
        card.addView(description, matchWrap());

        TextView author = new TextView(this);
        author.setText("Author: " + request.authorUsername + " (id " + request.authorId + ")");
        author.setTextSize(12);
        author.setTextColor(0xFF6B7280);
        card.addView(author, matchWrap());

        Button details = new Button(this);
        details.setText("Details");
        details.setAllCaps(false);
        details.setContentDescription("open_request_" + request.id);
        LinearLayout.LayoutParams detailsLp = matchWrap();
        detailsLp.topMargin = dp(6);
        card.addView(details, detailsLp);

        Button delete = new Button(this);
        delete.setText("Delete");
        delete.setAllCaps(false);
        delete.setContentDescription("delete_request_" + request.id);
        LinearLayout.LayoutParams deleteLp = matchWrap();
        deleteLp.topMargin = dp(2);
        card.addView(delete, deleteLp);

        details.setOnClickListener(v -> {
            setStatus("Loading request #" + request.id + "…");
            api.getRequest(request.id, new ApiClient.Callback<ApiClient.RequestItem>() {
                @Override
                public void onSuccess(ApiClient.RequestItem result) {
                    showRequestDetails(result);
                    clearStatus();
                }

                @Override
                public void onError(String message) {
                    setStatus(message);
                }
            });
        });

        delete.setOnClickListener(v -> {
            setStatus("Deleting request #" + request.id + "…");
            api.deleteRequest(request.id, new ApiClient.Callback<String>() {
                @Override
                public void onSuccess(String result) {
                    setStatus("Deleted request #" + request.id + ".");
                    loadRequests(list);
                }

                @Override
                public void onError(String message) {
                    setStatus(message);
                }
            });
        });
    }
}
