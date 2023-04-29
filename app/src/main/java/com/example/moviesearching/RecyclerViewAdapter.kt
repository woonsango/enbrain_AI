package com.example.moviesearching

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.moviesearching.databinding.ActivityRecyclerViewBinding

// ArrayList<모델 클래스>: 모델 클래스를 불러와서 리스트화 시킴.
// : 다음에 오는 것은 상속받을 틀.
class RecyclerViewAdapter(val itemList: ArrayList<ListItem>) : RecyclerView.Adapter<RecyclerViewAdapter.ProfileViewHolder>(){
    class ProfileViewHolder(val binding: ActivityRecyclerViewBinding) : RecyclerView.ViewHolder(binding.root)

//    init {
//        for (i in 0 until itemList.size) {
//            val item = ListItem(itemList[i].title)
//            this.itemList.add(item)
//        }
//    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProfileViewHolder {
        println("onCreateViewwHolder")
        for(i in 0 until this.itemList.size) {
            println(itemList[i].title);
        }
        // 변수 view: list_item_movie의 정보를 가져와서 어뎁터와 연결.
        val view = LayoutInflater.from(parent.context).inflate(R.layout.activity_recycler_view, parent, false)
        return ProfileViewHolder(ActivityRecyclerViewBinding.bind(view))
    }

    override fun getItemCount(): Int {
        return itemList.size
    }

    // 리스트뷰를 계속 사용할 때, onBindViewHolder가 지속적으로 호출이 되면서 모든 데이터들을 연결.
    override fun onBindViewHolder(holder: ProfileViewHolder, position: Int) {
        println(position)
        holder.binding.tvMovie.text = itemList.get(position).title
    }

}