package com.example.moviesearching

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.moviesearching.databinding.ActivityMainBinding
import com.example.moviesearching.databinding.ActivitySubBinding

class SubActivity : AppCompatActivity() {
    private lateinit var binding: ActivitySubBinding
    private var titleList: ArrayList<String> = ArrayList()
    private var ex: ArrayList<ListItem> = ArrayList()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySubBinding.inflate(layoutInflater)
        setContentView(binding.root)

        if(intent.hasExtra("movieTitle")) {
            var title = intent.getSerializableExtra("movieTitle") as String
            binding.tvTest.text = title
        }


        // MainActivity에서 "titleList" 값을 전달받아서 "ex" ArrayList에 추가합니다.
        if (intent.hasExtra("titleList")){
            println("Title List existed!")
            val titleListObj = intent.getSerializableExtra("titleList") as TitleList
            val titleList = titleListObj.titles
            val ex = ArrayList<ListItem>()
            for (title in titleList) {
                ex.add(ListItem(title))
            }
            binding.rvMovieList.adapter = RecyclerViewAdapter(ex)
        }

        // RecyclerView 설정

        binding.rvMovieList.layoutManager = LinearLayoutManager(this, LinearLayoutManager.VERTICAL, false)
        binding.rvMovieList.setHasFixedSize(true)
//        binding.rvMovieList.adapter = RecyclerViewAdapter(ex)
    }
}
