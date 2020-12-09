import React, { Component } from "react";
import { Card, Button, Row, Col, Container, Image, Accordion } from "react-bootstrap";
import HeaderHR from "../Header/HeaderHR";
import ls from "local-storage";
import { MDBIcon } from "mdbreact";

class viewApplications extends Component {
  constructor() {
    super();
    this.state = {
      applications: [],
      index: 0,
      view: [],
      started: false,
      completed: false,
      modal_message: "",
      modal_show: false
    };
  }

  componentDidMount() {
    const userId = ls.get("userid")
    const token = ls.get("token");
    console.log(token)
    fetch("http://localhost:5000/api/v1/getAllPresence/"+ userId + "/",
      {
        headers: {
          "Authorization": "Bearer " + token
        }
      })
      .then((response) => response.json())
      .then((res) => {

        if (res["results"]) {
          this.setState({ applications: res["results"] });
        }
        // else {
        //   this.modalShow(res["error"])
        // }
      });
  }
  modalShow = (message) => {
    this.setState({ modal_show: true, modal_message: message });
  };
  next = () => {
    if(this.state.index < (this.state.applications.length - 1)){
      const newIndex = this.state.index + 1;
      const newApplication = this.state.applications[newIndex];

      const newView = []
      newView[0] = newApplication

      this.setState({
        index: newIndex,
        view: newView
      });
      
    } else {
      const newView = []
      this.setState({
        view: newView,
        completed: true
      })
    }   
  }
  updateReviewerDetails(status){
    const reviewerDetails = {
      reviewer_id: ls.get("userid"),
      application_status: status,
    };
    const data = {
      user_id: this.state.applications[this.state.index].user_id,
      profile_id: this.state.applications[this.state.index].profile_id,
      feedback: reviewerDetails,
    };
    fetch("http://localhost:5000//api/v1/savePresenceReview/", {
        method: "PATCH",
        headers: {
          "Content-type": "application/json",
        },
        body: JSON.stringify(data),
      });
  }
  handleAccept = (e) => {
    this.updateReviewerDetails("Accepted");
    this.next();
    console.log("Accepting application"); 
  };

  handleDecline = (e) => {
    this.updateReviewerDetails("Declined");
    this.next();
    console.log("Declining application");
  };

  start = (e) => {
    if(this.state.applications.length>0){
    const newApplication = this.state.applications[this.state.index];

    const newView = []
    newView[0] = newApplication

    this.setState({
      view: newView,
      started: true
    });
  }
  else{
    const newView = []
      this.setState({
        view: newView,
        started: true,
        completed: true
      })
    // this.modalShow("No presences to be reviewed!");
  }
  };

  render() {
    return (
      <>
      <style type="text/css">
          {`
            .card-title {
              margin-bottom: 0rem;
            }
            .h5 {
              margin-bottom: 0rem;
            }
          `}
        </style>
      <div>
        <HeaderHR />
        {this.state.started ? "": 
            (
              <Container>
                <h4 className="text-center">A set of applications will be displayed. You will choose to accept or decline them.</h4> <br />

                <h5 className="text-center">Press Start to begin processing applications</h5>
                <br />
                <div class="d-flex justify-content-center">
                <Button id="start" variant="success" size="lg" onClick={this.start} class="btn btn-default">Start</Button>
                </div>
              </Container>
             )}

        {this.state.completed ? 
            (
              <Container>
                <h3> Completed. No more applications to assess. </h3> 
              </Container>
            ) 
            : ""}
        
        {this.state.view.map((a) => (
            <Container className="containbody justify-content-center">
              <div>
                <h1> {a.first_name} {a.last_name} </h1>
                <h5> Position sought: {a.position}</h5>
                <h5> Email: {a.email} </h5>
              </div>
            

            <Row>
              <Col>
                <Card.Title className="card-heading card-title h5 font-weight-bold">
                  ABOUT ME
                </Card.Title>
                <Card bg="Light">
                  <Card.Body>
                    <Row>
                      <Col sm={8}>
                        <h5> Location: {a.city}, {a.state}, {a.zip} </h5>
                        <br />
                        <label id="aboutMe">{a.about_me}</label>
                      </Col>
                      <Col sm={3}>
                        <Image
                          className="image-style"
                          src={a.profile_image}
                          roundedCircle
                        ></Image>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
            <br />

            <Row>
              <Col>
                <Accordion defaultActiveKey="0">
                  <Card.Title className="card-heading">EDUCATION</Card.Title>
                  {a.education.map((edu, i) => (
                    <Card>
                      <Accordion.Toggle as={Card.Header} eventKey={i + 1}>
                          <strong> {edu.school} </strong> <br /> {edu.degree} in{" "}
                          {edu.major}
                      </Accordion.Toggle>
                      <Accordion.Collapse eventKey={i + 1}>
                        <Card.Body>
                          <Card.Text>
                            {edu.eduStartDate} to {edu.eduEndDate} <br />
                            GPA: {edu.gpa}
                          </Card.Text>
                        </Card.Body>
                      </Accordion.Collapse>
                    </Card>
                  ))}
                </Accordion>
              </Col>

              <Col>
                <Accordion defaultActiveKey="0">
                  <Card.Title className="card-heading">EXPERIENCE</Card.Title>
                  {a.experience.map((exp, i) => (
                    <Card>
                      <Accordion.Toggle as={Card.Header} eventKey={i + 1}>
                          <strong>
                              {exp.company} {exp.title}
                          </strong>
                          <br />
                          {exp.duration}
                      </Accordion.Toggle>
                      <Accordion.Collapse eventKey={i + 1}>
                        <Card.Body>
                          <Card.Text>
                            {exp.expStartDate} to {exp.expEndDate} <br />
                            Location: {exp.location}
                          </Card.Text>
                        </Card.Body>
                      </Accordion.Collapse>
                    </Card>
                  ))}
                </Accordion>
              </Col>
            </Row>
            
            <br />
              <Row>
                <Col></Col>
                <Col>
                  <Button id="accept" variant="success" size="lg" onClick={this.handleAccept} block>Accept</Button>
                </Col>
                <Col>
                </Col>
                <Col> 
                  <Button id="decline" variant="danger" size="lg" onClick={this.handleDecline} block>Decline</Button>
                </Col>
                <Col></Col>
              </Row>        
            <br />
            
            </Container>
        ))}
        <br />
        
      </div>

      </>
    );
  }
}
export default viewApplications;
