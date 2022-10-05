import * as React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Page extends React.Component {
  /* Display a page of results
             */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      next: '',
      morePosts: true,
      posts: [],
    };
    this.fetchMoreData = this.fetchMoreData.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    console.log('MOUNTING COMPONENT');

    // Call REST API to get the page's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          posts: [
            ...prevState.posts,
            ...data.results,
          ],
          next: data.next,
        }));
        if (data.next === '') {
          this.setState({
            morePosts: false,
          });
        }
      })
      .catch((error) => console.log(error));
  }

  fetchMoreData() {
    const { next } = this.state;
    /*
    // a fake async api call like which sends
    // 20 more records in 1.5 secs
    setTimeout(() => {
        this.setState({
            items: this.state.items.concat(Array.from({ length: 20 }))
        });
    }, 1500);
    */
    console.log(next);
    // Call REST API to get the post's information
    fetch(next, {
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          posts: [
            ...prevState.posts,
            ...data.results,
          ],
          next: data.next,
        }));
        if (data.next === '') {
          this.setState({
            morePosts: false,
          });
        }
      })
      .catch((error) => console.log(error));
  }

  render() {
    let { posts, morePosts } = this.state;
    window.onbeforeunload = window.history.pushState({ posts, morePosts }, '');
    const navEntries = window.performance.getEntriesByType('navigation');
    if (navEntries.length > 0 && navEntries[0].type === 'back_forward') {
      const prevState = window.history.state;
      posts = prevState.posts;
      morePosts = prevState.morePosts;
    }

    const postList = posts.map((post) => (
      <Post url={post.url} key={post.postid} />
    ));

    return (
      <InfiniteScroll
        dataLength={posts.length}
        next={this.fetchMoreData}
        hasMore={morePosts}
        loader={<h4>Loading...</h4>}
      >
        {postList}
      </InfiniteScroll>
    );
  }
}

Page.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Page;
