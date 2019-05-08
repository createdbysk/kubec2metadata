import pytest

class TestEventHandlerChain(object):
    @pytest.fixture()
    def pod_event_handler_chain_factory(self):
        def factory(*args):
            import event_handlers
            instance = event_handlers.PodEventHandlerChain(*args)
            return instance
        yield factory

    @pytest.mark.parametrize("handled_by_1, handled_by_2", [
        (False, False),
        (True, False),
        (False, True)
    ])
    def test_event_handler_chain_handle(self, 
                                        handled_by_1,
                                        handled_by_2,
                                        pod_event_handler_chain_factory,
                                        v1pod,
                                        mocker):
        # GIVEN
        class EventHandlerSpec(object):
            def handle(self):
                raise NotImplementedError()

        event_handler1 = mocker.Mock(spec=EventHandlerSpec)
        event_handler1.handle.return_value = handled_by_1
        event_handler2 = mocker.Mock(spec=EventHandlerSpec)
        event_handler2.handle.return_value = handled_by_2
        
        pod_event_handler_chain = pod_event_handler_chain_factory(
            event_handler1,
            event_handler2
        )
        
        # If at least one event handler will handle the event,
        # then the expected result will be True,
        # False otherwise.
        expected_result = handled_by_1 or handled_by_2

        # WHEN
        actual_result = pod_event_handler_chain.handle(v1pod)

        # THEN
        event_handler1.handle.assert_called_with(v1pod)
        if not handled_by_1:
            event_handler2.handle.assert_called_with(v1pod)
        else:
            event_handler2.handle.assert_not_called()

        assert expected_result == actual_result

