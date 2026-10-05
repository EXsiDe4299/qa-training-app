package com.example.qatrainingapp;

import android.os.Handler;
import android.os.Looper;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.CookieHandler;
import java.net.CookieManager;
import java.net.CookiePolicy;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ApiClient {
    public interface Callback<T> {
        void onSuccess(T result);
        void onError(String message);
    }

    public static class User {
        public final int id;
        public final String username;

        public User(int id, String username) {
            this.id = id;
            this.username = username;
        }
    }

    public static class RequestItem {
        public final int id;
        public final String title;
        public final String description;
        public final int authorId;
        public final String authorUsername;

        public RequestItem(int id, String title, String description, int authorId, String authorUsername) {
            this.id = id;
            this.title = title;
            this.description = description;
            this.authorId = authorId;
            this.authorUsername = authorUsername;
        }
    }

    public static class LoginResult {
        public final int userId;
        public final String username;

        public LoginResult(int userId, String username) {
            this.userId = userId;
            this.username = username;
        }
    }

    private static class RawResponse {
        final int statusCode;
        final String body;

        RawResponse(int statusCode, String body) {
            this.statusCode = statusCode;
            this.body = body;
        }
    }

    private interface Parser<T> {
        T parse(RawResponse response) throws Exception;
    }

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final CookieManager cookieManager;
    private String baseUrl;

    public ApiClient(String baseUrl) {
        cookieManager = new CookieManager(null, CookiePolicy.ACCEPT_ALL);
        CookieHandler.setDefault(cookieManager);
        setBaseUrl(baseUrl);
    }

    public void setBaseUrl(String value) {
        baseUrl = value == null ? "" : value.trim();
        while (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
        }
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public void clearCookies() {
        cookieManager.getCookieStore().removeAll();
    }

    public void login(String username, String password, Callback<LoginResult> callback) {
        JSONObject body = new JSONObject();
        try {
            body.put("username", username);
            body.put("password", password);
        } catch (Exception e) {
            postError(callback, e.getMessage());
            return;
        }

        requestAsync("POST", "/api/v1/auth/login", body.toString(), callback, response -> {
            JSONObject json = new JSONObject(response.body);
            return new LoginResult(json.getInt("user_id"), json.getString("username"));
        });
    }

    public void register(String username, String password, Callback<User> callback) {
        JSONObject body = new JSONObject();
        try {
            body.put("username", username);
            body.put("password", password);
        } catch (Exception e) {
            postError(callback, e.getMessage());
            return;
        }

        requestAsync("POST", "/api/v1/users/register", body.toString(), callback, response -> {
            JSONObject json = new JSONObject(response.body);
            return new User(json.getInt("id"), json.getString("username"));
        });
    }

    public void logout(Callback<String> callback) {
        requestAsync("POST", "/api/v1/auth/logout", null, callback, response -> {
            String message = "Logged out";
            if (!response.body.isEmpty()) {
                JSONObject json = new JSONObject(response.body);
                if (json.has("message")) {
                    message = json.getString("message");
                }
            }
            clearCookies();
            return message;
        });
    }

    public void me(Callback<User> callback) {
        requestAsync("GET", "/api/v1/auth/me", null, callback, response -> {
            JSONObject json = new JSONObject(response.body);
            return new User(json.getInt("id"), json.getString("username"));
        });
    }

    public void getRequest(int requestId, Callback<RequestItem> callback) {
        requestAsync("GET", "/api/v1/requests/" + requestId, null, callback, response -> {
            JSONObject json = new JSONObject(response.body);
            return new RequestItem(
                    json.getInt("id"),
                    json.getString("title"),
                    json.getString("description"),
                    json.getInt("author_id"),
                    json.getString("author_username")
            );
        });
    }

    public void getRequests(Callback<List<RequestItem>> callback) {
        requestAsync("GET", "/api/v1/requests", null, callback, response -> {
            JSONArray array = new JSONArray(response.body);
            List<RequestItem> result = new ArrayList<>();
            for (int i = 0; i < array.length(); i++) {
                JSONObject json = array.getJSONObject(i);
                result.add(new RequestItem(
                        json.getInt("id"),
                        json.getString("title"),
                        json.getString("description"),
                        json.getInt("author_id"),
                        json.getString("author_username")
                ));
            }
            return result;
        });
    }

    public void createRequest(String title, String description, Callback<RequestItem> callback) {
        JSONObject body = new JSONObject();
        try {
            body.put("title", title);
            body.put("description", description);
        } catch (Exception e) {
            postError(callback, e.getMessage());
            return;
        }

        requestAsync("POST", "/api/v1/requests", body.toString(), callback, response -> {
            JSONObject json = new JSONObject(response.body);
            return new RequestItem(
                    json.getInt("id"),
                    json.getString("title"),
                    json.getString("description"),
                    json.getInt("author_id"),
                    json.getString("author_username")
            );
        });
    }

    public void deleteRequest(int requestId, Callback<String> callback) {
        requestAsync("DELETE", "/api/v1/requests/" + requestId, null, callback, response -> {
            if (response.body == null || response.body.isEmpty()) {
                return "Request deleted";
            }
            try {
                JSONObject json = new JSONObject(response.body);
                return json.has("message") ? json.getString("message") : response.body;
            } catch (Exception ignored) {
                return response.body;
            }
        });
    }

    private <T> void requestAsync(String method, String path, String body,
                                  Callback<T> callback, Parser<T> parser) {
        executor.execute(() -> {
            try {
                RawResponse response = executeRequest(method, path, body);
                if (response.statusCode < 200 || response.statusCode >= 300) {
                    throw new IOException(formatHttpError(response.statusCode, response.body));
                }
                T result = parser.parse(response);
                postSuccess(callback, result);
            } catch (Exception e) {
                postError(callback, formatError(e));
            }
        });
    }

    private RawResponse executeRequest(String method, String path, String body) throws IOException {
        if (baseUrl.isEmpty()) {
            throw new IOException("API URL is empty");
        }

        URL url = new URL(baseUrl + path);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod(method);
        connection.setConnectTimeout(7000);
        connection.setReadTimeout(10000);
        connection.setUseCaches(false);
        connection.setRequestProperty("Accept", "application/json");

        if (body != null) {
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
            byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
            try (OutputStream output = connection.getOutputStream()) {
                output.write(bytes);
            }
        }

        int status = connection.getResponseCode();
        InputStream stream = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
        String responseBody = stream == null ? "" : readAll(stream);
        connection.disconnect();
        return new RawResponse(status, responseBody);
    }

    private String readAll(InputStream inputStream) throws IOException {
        StringBuilder builder = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
        }
        return builder.toString();
    }

    private String formatHttpError(int statusCode, String responseBody) {
        if (responseBody == null || responseBody.isEmpty()) {
            return "HTTP " + statusCode;
        }
        return "HTTP " + statusCode + ": " + responseBody;
    }

    private String formatError(Exception e) {
        String message = e.getMessage();
        return message == null || message.isEmpty() ? e.getClass().getSimpleName() : message;
    }

    private <T> void postSuccess(Callback<T> callback, T result) {
        mainHandler.post(() -> callback.onSuccess(result));
    }

    private <T> void postError(Callback<T> callback, String message) {
        mainHandler.post(() -> callback.onError(message == null ? "Unknown error" : message));
    }

    public void shutdown() {
        executor.shutdownNow();
    }
}
