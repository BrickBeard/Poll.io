var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var browserHistory = ReactRouter.browserHistory;

// CSS style to align text to the center of it's container
var Align = {
  textAlign: "center",
  fontFamily: "EB Garamond"
};
var origin = window.location.origin;

try {
  var SimpleTimePicker = ReactSimpleTimePicker.SimpleTimePicker;
} catch(err){
  console.log(err);
}

var PollForm = React.createClass({
  getInitialState: function(e) {
    // Set initial state of form inputs

    // close poll in 24 hours by default
    var close_date = new Date();
    close_date.setHours(close_date.getHours() + 24);
    close_date = close_date.getTime() / 1000;

    return { title: "", option: "", options: [], close_date, all_options: [] };
  },

  onDateChange: function(e){
    var close_date = e.getTime() / 1000

    this.setState({close_date: close_date})
  },

  handleTitleChange: function(e) {
    // Change title as the user types
    this.setState({ title: e.target.value });
  },

  handleOptionChange: function(e) {
    this.setState({ option: e.target.value });
  },

  handleOptionAdd: function(e) {
    // Update poll options and reset options to an empty string
    this.setState({
      options: this.state.options.concat({ name: this.state.option }),
      option: ""
    });
  },

  componentDidMount: function() {
    var url = origin + "/api/polls/options";

    $.ajax({
      url: url,
      dataType: "json",
      cache: false,
      success: function(data) {
        console.log(data);
        this.setState({ all_options: data });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  handleSubmit: function(e) {
    e.preventDefault();
    var title = this.state.title;
    var options = this.state.options;
    var close_date = this.state.close_date;

    var data = {
      title: title,
      options: options.map(function(x) {
        return x.name;
      }),
      close_date: close_date
    };
    var url = origin + "/api/polls";

    // make post request
    $.ajax({
      url: url,
      dataType: "json",
      type: "POST",
      data: JSON.stringify(data),
      contentType: "application/json; charset=utf-8",
      success: function(data) {
        alert(data.message);
      }.bind(this),
      error: function(xhr, status, err) {
        alert("Poll creation failed: " + err.toString());
      }.bind(this)
    });
  },

  render: function() {
    var classContext = "col-sm-6 col-sm-offset-3";
    var all_options = this.state.all_options.map(function(option) {
      return <option key={option.id} value={option.name} />;
    });
    return (
      <div>
        <form
          className="form-signin"
          id="poll_form"
          onSubmit={this.handleSubmit}
        >
          <h2 className="form-signin-heading" style={Align}>
            Create a Poll
          </h2>

          <div className="form-group has-success">
            <label htmlFor="title" className="sr-only">
              Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              className="form-control"
              placeholder="Title"
              onChange={this.handleTitleChange}
              required
              autoFocus
            />
          </div>

          <div className="form-group has-success">
            <label htmlFor="option" className="sr-only">
              Option
            </label>
            <input
              list="option"
              className="form-control"
              placeholder="Option"
              onChange={this.handleOptionChange}
              value={this.state.option ? this.state.option : ""}
              autoFocus
            />
          </div>

          <datalist id="option">{all_options}</datalist>

          <SimpleTimePicker days="7" onChange={this.onDateChange} />
          <br />

          <div className="row form-group">
            <button
              type="button"
              className="btn btn-lg btn-success btn-block"
              onClick={this.handleOptionAdd}
            >
              Add Option
            </button>
            <button className="btn btn-lg btn-success btn-block" type="submit">
              Save Poll
            </button>
          </div>
          <br />
        </form>
        <div className="row">
          <h3 style={Align}>Live Preview</h3>
          <LivePreview
            title={this.state.title}
            options={this.state.options}
            classContext={classContext}
          />
        </div>
      </div>
    );
  }
});

var LivePreview = React.createClass({
  getInitialState: function() {
    return { selected_option: "", disabled: 0 };
  },

  handleOptionChange: function(e) {
    this.setState({ selected_option: e.target.value });
  },

  voteHandler: function(e) {
    e.preventDefault();

    var data = {
      poll_title: this.props.title,
      option: this.state.selected_option
    };

    this.props.voteHandler(data);

    this.setState({ disabled: 1 });
  },

  render: function() {
    var options = this.props.options.map(
      function(option) {
        if (option.name) {
          var progress =
            Math.round(
              (option.vote_count / this.props.total_vote_count) * 100
            ) || 0;
          var current = { width: progress + "%" };

          return (
            <div key={option.name}>
              <input
                type="radio"
                name="options"
                value={option.name}
                onChange={this.handleOptionChange}
              />{" "}
              {option.name}
              <div className="progress">
                <div
                  className="progress-bar progress-bar-success"
                  role="progressbar"
                  aria-valuenow={progress}
                  aria-valuemin="0"
                  aria-valuemax="100"
                  style={current}
                >
                  {progress}%
                </div>
              </div>
            </div>
          );
        }
      }.bind(this)
    );

    return (
      <div className={this.props.classContext}>
        <div className="panel panel-success">
          <div className="panel-heading">
            <h4>{this.props.title}</h4>
          </div>
          <div className="panel-body">
            <form onSubmit={this.voteHandler}>
              {options}
              <br />
              <button
                type="submit"
                disabled={this.state.disabled}
                className="btn btn-success btn-outline hvr-grow"
              >
                Vote!
              </button>
              <small>{this.props.total_vote_count} votes so far</small>
            </form>
          </div>
        </div>
      </div>
    );
  }
});

var LivePreviewProps = React.createClass({
  voteHandler: function(data) {
    var url = origin + "/api/poll/vote";

    $.ajax({
      url: url,
      dataType: "json",
      type: "PATCH",
      data: JSON.stringify(data),
      contentType: "application/json; charset=utf-8",
      success: function(data) {
        alert(data.message);
        this.setState({ selected_option: "" });
        this.props.loadPollsFromServer();
      }.bind(this),
      error: function(xhr, status, err) {
        alert("Poll creation failed: " + err.toString());
      }.bind(this)
    });
  },

  render: function() {
    var polls = this.props.polls.Polls.map(
      function(poll) {
        return (
          <LivePreview
            key={poll.title}
            title={poll.title}
            options={poll.options}
            total_vote_count={poll.total_vote_count}
            voteHandler={this.voteHandler}
            classContext={this.props.classContext}
          />
        );
      }.bind(this)
    );
    return (
      <div>
        <h1 style={Align}>{this.props.header}</h1>
        <br />
        <div className="row">{polls}</div>
      </div>
    );
  }
});

var AllPolls = React.createClass({
  getInitialState: function() {
    return { polls: { Polls: [] }, header: "", classContext: "" };
  },

  loadPollsFromServer: function() {
    var pollName = this.props.routeParams.pollName;

    if (pollName) {
      var url = origin + "/api/poll/" + pollName;
      this.setState({ classContext: "col-sm-6 col-sm-offset-3" });
    } else {
      var url = origin + "/api/polls";
      this.setState({ header: "Latest polls", classContext: "col-sm-6" });
    }

    $.ajax({
      url: url,
      dataType: "json",
      cache: false,
      success: function(data) {
        this.setState({ polls: data });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  componentDidMount: function() {
    this.loadPollsFromServer();
  },

  render: function() {
    if (!this.state.polls.message) {
      return (
        <LivePreviewProps
          polls={this.state.polls}
          loadPollsFromServer={this.loadPollsFromServer}
          header={this.state.header}
          classContext={this.state.classContext}
        />
      );
    } else {
      return (
        <div style={Align}>
          <h1>Poll not found</h1>
          <p>
            You might be interested in these <a href="/">polls</a>
          </p>
        </div>
      );
    }
  }
});

ReactDOM.render(
  <Router history={browserHistory}>
    <Route path="/" component={AllPolls} />
    <Route path="/polls" component={PollForm} />
    <Route path="/polls/:pollName" component={AllPolls} />
  </Router>,
  document.getElementById("container")
);
