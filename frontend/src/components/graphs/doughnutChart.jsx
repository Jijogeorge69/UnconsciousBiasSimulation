import React from "react";
import { Doughnut } from "react-chartjs-2";
import { Col, Row, Container } from "react-bootstrap";

class DoughnutChart extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataDoughnut: this.props.inputData
        }
    }

    render() {
        return (
            <Container>
                <br />
                <Row>
                    <Col></Col>
                    <Col xs={10}>
                        <Doughnut data={this.state.dataDoughnut} options={{ responsive: true }} />
                    </Col>
                    <Col></Col>
                </Row>
                <br />
            </Container>

        );
    }
}

export default DoughnutChart;