package com.example.moviesearching

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.StrictMode
import android.util.Log
import com.example.moviesearching.databinding.ActivityMainBinding
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.FileDescriptor.out
import java.net.HttpURLConnection
import java.net.URL
import java.io.Serializable

data class TitleList(val titles: ArrayList<String>) : Serializable
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder().permitAll().build())

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.button.setOnClickListener {
            val movietitle = binding.movietitle.text.toString() // EditText에서 텍스트 가져오기


            try {
                var json = JSONObject()
                json.put("title", movietitle);

                val conn = URL("http://10.30.116.62:8000/api/movies/").openConnection() as HttpURLConnection
                conn.doOutput = true
                conn.requestMethod = "POST"
                conn.addRequestProperty("Content-Type", "application/json")

                val output = conn.outputStream
                output.write(json.toString().toByteArray())
                output.flush()
                output.close()

                conn.inputStream.use { `in` ->
                    ByteArrayOutputStream().use { out ->
                        val buf = ByteArray(1024 * 8)
                        var length = 0
                        while (`in`.read(buf).also { length = it } != -1) {
                            out.write(buf, 0, length)
                        }
                        val response = String(out.toByteArray())
                        val jsonObject = JSONObject(response)
                        val titleList = jsonObject.getJSONArray("title")
                        val titles = ArrayList<String>()
                        for (i in 0 until titleList.length()){
                            val title = titleList.getString(i)
                            Log.d("test", title)
                            titles.add(title)
                        }
                        val titleListObj = TitleList(titles)
//                        val jsonResponse = JSONARRA(response)
//                        val titles = .getJSONArray("title")
//                        for (i in 0 until titles.length()) {
//                            val title = titles.getJSONObject(i)
//                            Log.d("test", title.getString("title"))
//                        }
                        val intent = Intent(this, SubActivity::class.java).apply {
                            putExtra("movieTitle", movietitle)
                            putExtra("titleList", titleListObj) // movietitle 추가
                        }
                        startActivity(intent) // SubActivity 시작
                    }
                }
            } catch (e: Exception) {
                println(e)
            }

        }
    }
}