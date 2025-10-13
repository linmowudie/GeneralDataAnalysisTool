from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from api.session_manager import session_manager
from Src.DataAnalyzer.Configs.log_setting import get_component_logger

# 配置API日志
api_logger = get_component_logger('api', 'step_lock')

# 创建路由器
router = APIRouter(tags=['步骤锁管理'])

@router.post('/api/step/lock', response_model=Dict[str, Any])
async def lock_step(
    session_id: str = Query(..., description='会话ID'),
    step: str = Query(..., description='要锁定的步骤名称')
):
    """
    锁定指定的步骤
    
    该API用于锁定数据处理流程中的特定步骤，防止其被意外修改。
    可用的步骤名称包括：import, preview, cleaning, analysis, visualization, report
    
    Args:
        session_id: 会话ID
        step: 要锁定的步骤名称
    
    Returns:
        dict: 包含操作结果和当前锁定状态的字典
    
    Raises:
        HTTPException: 当会话ID不存在或步骤名称无效时
    """
    try:
        # 验证步骤名称是否有效
        valid_steps = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report']
        if step not in valid_steps:
            api_logger.warning(f"无效的步骤名称: {step}")
            raise HTTPException(status_code=400, detail=f"无效的步骤名称: {step}。有效步骤: {valid_steps}")
        
        # 获取会话引擎
        engine = session_manager.get_engine(session_id)
        
        # 锁定步骤
        engine.lock_step(step)
        
        # 获取更新后的步骤状态
        status = engine.get_step_status()
        
        api_logger.info(f"会话 {session_id} 的步骤 {step} 已锁定")
        return {
            'status': 'success',
            'message': f'步骤 {step} 已成功锁定',
            'locked_steps': status['locked_steps']
        }
    except ValueError as e:
        api_logger.error(f"锁定步骤失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        api_logger.error(f"锁定步骤时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"锁定步骤时发生错误: {str(e)}")

@router.post('/api/step/unlock', response_model=Dict[str, Any])
async def unlock_step(
    session_id: str = Query(..., description='会话ID'),
    step: str = Query(..., description='要解锁的步骤名称')
):
    """
    解锁指定的步骤
    
    该API用于解锁数据处理流程中已锁定的特定步骤，使其可以被修改。
    
    Args:
        session_id: 会话ID
        step: 要解锁的步骤名称
    
    Returns:
        dict: 包含操作结果和当前锁定状态的字典
    
    Raises:
        HTTPException: 当会话ID不存在或步骤名称无效时
    """
    try:
        # 验证步骤名称是否有效
        valid_steps = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report']
        if step not in valid_steps:
            api_logger.warning(f"无效的步骤名称: {step}")
            raise HTTPException(status_code=400, detail=f"无效的步骤名称: {step}。有效步骤: {valid_steps}")
        
        # 获取会话引擎
        engine = session_manager.get_engine(session_id)
        
        # 移除锁定的步骤
        if step in engine.locked_steps:
            engine.locked_steps.remove(step)
        
        # 获取更新后的步骤状态
        status = engine.get_step_status()
        
        api_logger.info(f"会话 {session_id} 的步骤 {step} 已解锁")
        return {
            'status': 'success',
            'message': f'步骤 {step} 已成功解锁',
            'locked_steps': status['locked_steps']
        }
    except ValueError as e:
        api_logger.error(f"解锁步骤失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        api_logger.error(f"解锁步骤时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"解锁步骤时发生错误: {str(e)}")

@router.get('/api/step/status', response_model=Dict[str, Any])
async def get_step_status(
    session_id: str = Query(..., description='会话ID')
):
    """
    获取会话中所有步骤的状态
    
    该API用于获取数据处理流程中所有步骤的锁定和完成状态。
    
    Args:
        session_id: 会话ID
    
    Returns:
        dict: 包含已完成步骤和已锁定步骤的字典
    
    Raises:
        HTTPException: 当会话ID不存在时
    """
    try:
        status = session_manager.get_session_step_status(session_id)
        api_logger.info(f"获取会话 {session_id} 的步骤状态")
        return {
            'status': 'success',
            'data': status
        }
    except ValueError as e:
        api_logger.error(f"获取步骤状态失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        api_logger.error(f"获取步骤状态时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取步骤状态时发生错误: {str(e)}")

@router.post('/api/step/lock-multiple', response_model=Dict[str, Any])
async def lock_multiple_steps(
    session_id: str = Query(..., description='会话ID'),
    steps: List[str] = Query(..., description='要锁定的步骤名称列表')
):
    """
    同时锁定多个步骤
    
    该API用于一次性锁定数据处理流程中的多个步骤。
    
    Args:
        session_id: 会话ID
        steps: 要锁定的步骤名称列表
    
    Returns:
        dict: 包含操作结果和当前锁定状态的字典
    
    Raises:
        HTTPException: 当会话ID不存在或任何步骤名称无效时
    """
    try:
        # 验证步骤名称是否有效
        valid_steps = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report']
        invalid_steps = [step for step in steps if step not in valid_steps]
        
        if invalid_steps:
            api_logger.warning(f"无效的步骤名称: {invalid_steps}")
            raise HTTPException(status_code=400, detail=f"无效的步骤名称: {invalid_steps}。有效步骤: {valid_steps}")
        
        # 获取会话引擎
        engine = session_manager.get_engine(session_id)
        
        # 锁定所有步骤
        for step in steps:
            if step not in engine.locked_steps:
                engine.lock_step(step)
        
        # 获取更新后的步骤状态
        status = engine.get_step_status()
        
        api_logger.info(f"会话 {session_id} 的多个步骤已锁定: {steps}")
        return {
            'status': 'success',
            'message': f'{len(steps)} 个步骤已成功锁定',
            'locked_steps': status['locked_steps']
        }
    except ValueError as e:
        api_logger.error(f"锁定多个步骤失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        api_logger.error(f"锁定多个步骤时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"锁定多个步骤时发生错误: {str(e)}")